"""Build Nitro G3D Patricia dictionary nodes after changing entry membership."""
def rebuild_nodes(entries):
 if not entries:return
 keys=[int.from_bytes(n.encode("latin1").ljust(16,b"\0"),"little") for n,_ in entries]
 assert len(set(keys))==len(keys) and all(k>>127==0 for k in keys)
 nodes=[{"bit":127,"left":0,"right":0,"entry":0,"key":0}]
 def bit(key,n):return (key>>n)&1
 for i,key in enumerate(keys):
  parent=0;child=nodes[0]["left"]
  while nodes[parent]["bit"]>nodes[child]["bit"]:
   parent,child=child,nodes[child]["right" if bit(key,nodes[child]["bit"]) else "left"]
  diff=(key^nodes[child]["key"]).bit_length()-1;assert diff>=0
  parent=0;child=nodes[0]["left"]
  while nodes[parent]["bit"]>nodes[child]["bit"] and nodes[child]["bit"]>diff:
   parent,child=child,nodes[child]["right" if bit(key,nodes[child]["bit"]) else "left"]
  idx=len(nodes);direction=bit(key,diff)
  nodes.append({"bit":diff,"left":child if direction else idx,"right":idx if direction else child,"entry":i,"key":key})
  branch="left" if parent==0 else ("right" if bit(key,nodes[parent]["bit"]) else "left")
  nodes[parent][branch]=idx
 # ndspy emits the root with left-child1. Reorder nodes to satisfy it.
 first=nodes[0]["left"];order=[first]+[i for i in range(1,len(nodes)) if i!=first];remap={0:0,**{old:new for new,old in enumerate(order,1)}}
 for (_,obj),old in zip(entries,order):
  node=nodes[old];obj.unk00=node["bit"]|(remap[node["left"]]<<8);obj.unk02=remap[node["right"]]|(node["entry"]<<8)
 # Exercise the exact bitwise traversal and verify every final leaf.
 for i,key in enumerate(keys):
  parent=0;child=nodes[0]["left"]
  while nodes[parent]["bit"]>nodes[child]["bit"]:
   parent,child=child,nodes[child]["right" if bit(key,nodes[child]["bit"]) else "left"]
  assert nodes[child]["entry"]==i