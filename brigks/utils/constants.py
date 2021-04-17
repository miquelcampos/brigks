from math3d.vectorN import Vector3 


trs_attrs = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")
tr_attrs = ("tx", "ty", "tz", "rx", "ry", "rz")
ts_attrs = ("tx", "ty", "tz", "sx", "sy", "sz")
t_attrs = ("tx", "ty", "tz")
r_attrs = ("rx", "ry", "rz")

x_axis = Vector3([1,0,0])
y_axis = Vector3([0,1,0])
z_axis = Vector3([0,0,1])
nx_axis = Vector3([-1,0,0])
ny_axis = Vector3([0,-1,0])
nz_axis = Vector3([0,0,-1])
