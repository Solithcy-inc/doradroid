import doracoinsdatabase as dc
db=dc.connect()
cursor=db.cursor()

def giveitem(userid, item, amount):
    global cursor
    # check if user has a doracoins account
    print("SELECT userid, {} FROM inventory".format(item))
    cursor.execute(
        "SELECT userid, {} FROM inventory".format(item)
    )
    exists=False
    coins=0
    for i in cursor.fetchall():
        print(i)
        if str(i[0]) == str(userid):
            print(i)
            exists=True
            itemamount=i[1]
            break
    if exists:
        # user has account, update inventory
        cursor.execute(
            "UPDATE inventory SET {2} = {1} WHERE userid = {0};".format(str(userid),str(int(itemamount)+amount), item)
        )
    else:
        # user doesn't have an account, make one with the inventory
        cursor.execute(
            "INSERT INTO inventory (userid, {2}) VALUES ({0}, {1});".format(str(userid),str(amount), item)
        )

def getinv(userid):
    global cursor
    # check if user has a doracoins account
    cursor.execute(
        "SELECT * FROM inventory WHERE userid={}".format(str(userid))
    )
    records=cursor.fetchall()
    if records!=[]:
        j = 0
        dict1 = {}
        dict2 = {0:"", 1:"", 2:"psychrolutes", 3:"goldfish", 4:"carp", 5:"cod", 6:"haddock", 7:"siamese", 8:"pike", 9:"megamouth"}
        for i in records[0]:
            if j in [0,1]:
                pass
            else:
                dict1[dict2[j]]=i
            j+=1
        return dict1
    else:
        return {}

giveitem(330287319749885954, "psychrolutes", 1)
print(getinv(330287319749885954))
