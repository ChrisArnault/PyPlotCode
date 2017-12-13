
fname = input("filename ? ")
try:
    with open(fname) as f:
        line = f.readline()
except OSError:
    line = "EXCEPTION"

print(line)



