"""Shared player item storage using native HG field menus and bag selection.

Ten persistent stacks use otherwise unused saved variables 4152..4165.
No inventory is removed before storage capacity has been checked. Future
Pokémon Center integration should call this same script with these same vars.
"""
from opening import Script, end

SLOTS = [(0x4152+2*i, 0x4153+2*i) for i in range(10)]
INIT = 0x4166
TEXT = [
    'You turned on the PC.', '{PLAYER}\'s PC', 'SWITCH OFF',
    'ITEM STORAGE', 'WITHDRAW ITEM', 'DEPOSIT ITEM', 'TOSS ITEM', 'GO BACK',
    '{PLAYER} x{RIVAL}', 'CANCEL', 'How many?', '1', '5', '10', 'ALL',
    'The items were withdrawn.', 'The items were deposited.',
    'There is not enough room in your Bag.',
    'The PC can hold ten different items, with up to 999 of each.',
    'There are not that many items.', 'Toss these items?',
    'The items were discarded.', 'You turned off the PC.',
    "It's a Wii! Wii is huge in Kanto, too!",
    'Select an item from your Bag.', 'There are no items stored.',
    'What would you like to do?',
    'ITEMS', 'MEDICINE', 'POKE BALLS', 'TMs AND HMs', 'BERRIES',
    'MAIL', 'BATTLE ITEMS',
]


def message(s, index):
    # Don't overwrite the item/quantity buffers with player/rival names.
    s.emit(45); s.data.append(index)
    return s.emit(50).emit(53)


def menu(s, entries, *, result=0x800C):
    s.emit(45); s.data.append(26)
    s.emit(750); s.data.extend(bytes([1, 1, 0, 1])); s.emit(result)
    for text, value in entries:
        s.emit(751, text, 255, value)
    return s.emit(752).emit(53)


def buffer(s, opcode, slot, value):
    s.emit(opcode); s.data.append(slot); s.emit(value)
    return s


def script():
    s = Script().emit(96).emit(73, 1547)
    s.compare(INIT, 1).jump('boot', 1)
    for (item_var, qty_var), item, qty in zip(SLOTS, [17, 50], [1, 95]):
        s.emit(41, item_var, item).emit(41, qty_var, qty)
    s.emit(41, INIT, 1)
    s.label('boot'); message(s, 0)
    s.emit(746)
    s.label('main').emit(190); s.data.append(0)
    menu(s, [(1,0),(2,1)])
    s.compare(0x800C,0).jump('login',1).jump('exit')
    s.label('login').emit(73,1548)
    s.label('storage'); menu(s,[(4,0),(5,1),(6,2),(7,3)])
    for value, label in [(0,'withdraw'),(1,'deposit'),(2,'toss')]:
        s.compare(0x800C,value).jump(label,1)
    s.jump('main')
    for mode,label in [(0,'withdraw'),(2,'toss')]:
        s.label(label).emit(41,0x8008,mode).emit(41,0x8009,0)
        s.emit(45); s.data.append(26)
        s.emit(750); s.data.extend(bytes([1,1,0,1])); s.emit(0x8006)
        for i,(item_var,qty_var) in enumerate(SLOTS):
            s.compare(qty_var,0).jump(f'{label}_skip_{i}',1)
            buffer(s,194,0,item_var); buffer(s,198,1,qty_var)
            s.emit(751,8,255,i).emit(39,0x8009,1)
            s.label(f'{label}_skip_{i}')
        s.emit(751,9,255,250).emit(752).emit(53)
        # Menu's cancellation sentinel is FFFD, which also fails these cases.
        for i,(item_var,qty_var) in enumerate(SLOTS):
            s.compare(0x8006,i).jump(f'{label}_slot_{i}',1)
        s.jump('storage')
        for i,(item_var,qty_var) in enumerate(SLOTS):
            s.label(f'{label}_slot_{i}').emit(42,0x8004,item_var)
            s.emit(42,0x8005,qty_var).jump('quantity')
    s.label('deposit').emit(41,0x8008,1)
    menu(s,[(27+i,i) for i in range(7)]+[(9,250)],result=0x800A)
    s.compare(0x800A,6).jump('storage',2)
    message(s,24)
    s.emit(41,0x800B,0xCAFE).emit(333); s.data.append(0)
    s.emit(334,0x8004).emit(41,0x800B,0).emit(150)
    s.compare(0x8004,0).jump('storage',1)
    s.emit(130,0x8004,0x800C).compare(0x800C,7).jump('storage',1)
    s.emit(669,0x8004,0x8005)
    # Existing stack first; then the first empty stack.
    for i,(item_var,qty_var) in enumerate(SLOTS):
        s.emit(18,item_var,0x8004).jump(f'deposit_slot_{i}',1)
    for i,(item_var,qty_var) in enumerate(SLOTS):
        s.compare(qty_var,0).jump(f'deposit_slot_{i}',1)
    s.jump('full')
    for i,_ in enumerate(SLOTS):
        s.label(f'deposit_slot_{i}').emit(41,0x8006,i).jump('quantity')
    s.label('quantity'); message(s,10)
    menu(s,[(11,1),(12,5),(13,10),(14,0),(9,250)],result=0x8007)
    for qty in (1,5,10):
        s.compare(0x8007,qty).jump('quantity_ready',1)
    s.compare(0x8007,0).jump('all',1).jump('storage')
    s.label('all').emit(42,0x8007,0x8005)
    s.label('quantity_ready').emit(18,0x8007,0x8005).jump('insufficient',2)
    s.compare(0x8008,1).jump('do_deposit',1)
    s.compare(0x8008,2).jump('confirm_toss',1)
    s.emit(125,0x8004,0x8007,0x800C).compare(0x800C,0).jump('no_room',1)
    s.jump('subtract')
    s.label('confirm_toss'); s.emit(45);s.data.append(20)
    s.emit(63,0x800C).emit(53).compare(0x800C,0).jump('storage',5)
    s.label('subtract')
    for i,(_,qty_var) in enumerate(SLOTS):
        s.compare(0x8006,i).jump(f'subtract_{i}',1)
    s.jump('storage')
    for i,(item_var,qty_var) in enumerate(SLOTS):
        s.label(f'subtract_{i}').emit(40,qty_var,0x8007)
        s.compare(qty_var,0).jump(f'clear_{i}',1).jump('receipt')
        s.label(f'clear_{i}').emit(41,item_var,0).jump('receipt')
    s.label('do_deposit')
    for i,_ in enumerate(SLOTS):
        s.compare(0x8006,i).jump(f'add_{i}',1)
    s.jump('storage')
    for i,(item_var,qty_var) in enumerate(SLOTS):
        s.label(f'add_{i}').emit(42,0x8009,qty_var).emit(39,0x8009,0x8007)
        s.compare(0x8009,999).jump('full',2)
        s.emit(126,0x8004,0x8007,0x800C).compare(0x800C,0).jump('insufficient',1)
        s.emit(42,item_var,0x8004).emit(42,qty_var,0x8009).jump('receipt')
    s.label('receipt').emit(73,1500)
    for mode,msg in [(0,15),(1,16),(2,21)]:
        s.compare(0x8008,mode).jump(f'receipt_{mode}',1)
    s.jump('storage')
    for mode,msg in [(0,15),(1,16),(2,21)]:
        s.label(f'receipt_{mode}');message(s,msg);s.jump('storage')
    for label,msg in [('full',18),('insufficient',19),('no_room',17)]:
        s.label(label);message(s,msg);s.jump('storage')
    s.label('exit').emit(747).emit(73,1549);message(s,22)
    return end(s).finish()
