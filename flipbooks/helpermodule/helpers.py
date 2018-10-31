import random 

# See examples of these functions being used in views.py 

def string2List(stringyList):
    # assumes items are listed with "," only (for now)
    li = stringyList.split(",")
    
    #clean up
    return list( item.strip() for item in li )
    
def list2String(li):
    return ','.join(str(item) for item in li)

def order_by_id_ref(obj_li, ref_id_li):
   
    if not isinstance(ref_id_li, list):
        ref_id_li = string2List(ref_id_li)

    #make array same size as the object list
    print("ref_id_li: {}".format(ref_id_li))
    print("obj_li: {}".format(obj_li))
    obj_li_ordered = [None] * len(obj_li)
    
    for obj in obj_li:
        # Place obj in index matching its id in the ref list 
        # If not, value will remain None
        if str(obj.id) in ref_id_li:
            order_position = ref_id_li.index(str(obj.id))
            try: 
                obj_li_ordered[order_position] = obj
            except IndexError as error:
                print(error.args)
                print("Trying to place obj#{} at index {} out of {}.".format(obj.id, order_position, len(obj_li_ordered)))
                # if cannot handle: 
                #     raise
                raise
            
    return obj_li_ordered
    

def get_rand_base64(length):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    result_code = ''
    for i in range(length):
        result_code+=chars[random.randrange(0, len(chars))]

    return result_code

    
def shout():
    #for testing if this module is imported successfully
    print("Hello world!")
    



from ..models import (
    Book,
    Chapter,
    Scene,
    Strip,
    Frame
)


# -------------------------------------------
# -------------------------------------------
#           children_li helpers
# -------------------------------------------
# -------------------------------------------



''' Checks if children_li is valid. Currently used for custom tags.'''
# Accepts children_li in form of stringy list or a list
def is_valid_children_li(cli):
    
    if isinstance(cli, str) or isinstance(cli, str): # is it a string?
        # note, 'unicode' was renamed to 'str' in Python 3
        cli = cli.split(",")
    elif isinstance(cli, list): # is it a list?
        pass
    else: 
        return False
        
    cli = ''.join(cli)
    cli = cli.replace(" ","")
    if cli == '' : return False
    
    return True
        


''' The children_order may be blank or invalid. 
Use this function refresh/recreate the order based on
the order the children appears in db'''

def refresh_children_li(obj):
    
    children_li = None
    if isinstance(obj, Chapter):
        children_li = obj.scene_set.all()
    elif isinstance(obj, Scene):
        children_li = obj.strip_set.all()
    elif isinstance(obj, Strip):
        children_li = obj.frame_set.all()
    
    else:
        print("Not a valid object to extract children_li")
        return False
        
    #retrieve children
    children_id_li = [ch_obj.id for ch_obj in children_li]
    return ','.join(str(obj_id) for obj_id in children_id_li)



''' This children_order is just a stringy list that 
    changes very frequently. So mistakes can happen, like
    empty element, or extra element that is invalid '''
def cleanup_children_li(obj):

    children_ref = None
    child_inst_name = None

    if(isinstance(obj, Chapter)):
        children_ref = [str(scene.id) for scene in Scene.objects.filter(chapter=obj)]
        child_inst_name = "Scene"
    elif(isinstance(obj, Scene)):
        children_ref = [str(strip.id) for strip in Strip.objects.filter(scene=obj)]
        child_inst_name = "Strip"
    elif(isinstance(obj, Strip)):
        children_ref = [str(frame.id) for frame in Frame.objects.filter(strip=obj)]
        child_inst_name = "Frame"
    else:
        print("This instance does not have children_li")
        return ''

    cleaned_children_li = []
    
    children_li = obj.children_li.split(",")
    for child_id in children_li:
        is_valid = False
        child_id = str.strip(str(child_id))
        
        # Trial begins
        if child_id != '' and child_id == str(int(child_id)): #check if it is a valid integer

            try:   
                children_ref.remove(child_id) # this should check against duplicates
                is_valid = True
            except ValueError: 
                print("cleanup_children_li(): Ignoring foreign/duplicate id({}) of {} in children_li!".format(child_id,child_inst_name))
        
        if is_valid: cleaned_children_li.append(child_id)

    # Note: there may be a case where cleaned_children_li may have less children
    #       then the actual number of children. If this happens, it will be 
    #       noticed by the React app. Missing children will still render.


    return ','.join(str(child_id) for child_id in cleaned_children_li)







''' basically puts cleanup_children_li() and refresh_children_li() together  '''

def refresh_or_cleanup_children_li(obj):

    if(isinstance(obj, Chapter)):
        children_ref = [str(scene.id) for scene in Scene.objects.filter(chapter=obj)]
        child_inst_name = "Scene"
    elif(isinstance(obj, Scene)):
        children_ref = [str(strip.id) for strip in Strip.objects.filter(scene=obj)]
        child_inst_name = "Strip"
    elif(isinstance(obj, Strip)):
        children_ref = [str(frame.id) for frame in Frame.objects.filter(strip=obj)]
        child_inst_name = "Frame"
    else:
        print("This instance does not have children_li")
        return ''


    
    if obj.children_li == '' or obj.children_li == "False" or "".join(obj.children_li.split(","))== '':
        # Case 1: Check if valid children_li exists:
        print("[refresh_or_cleanup_children_li()]. Refreshing children_li.")
        new_children_li = refresh_children_li(obj)

        if new_children_li:
            return new_children_li
        else:
            return obj.children_li

    else:
        # Case 2: clean up preexisting children_li
        # Remember to query it RIGHT
        cleaned_children_li = cleanup_children_li(obj)

        if cleaned_children_li:
            return cleaned_children_li
        else:
            return obj.children_li







''' Updates children_li. This function most likely runs when save()
    Note: the insert_at number describes 'position', starts from 1.
          Make sure to -1 when using as an index, which starts from 0.
          
          '-1' = append at end
          '0' = no change in order'''

def update_children_li(obj, target_child_id, insert_at):
    
    new_children_li = []
    
    # if object's order_list is empty, 
    # it means it was never initialized or there is a problem
    if obj.children_li == "":
        new_children_li = refresh_children_li(obj) #Make new list by id
        new_children_li = new_children_li.split(",")
    else: 
        new_children_li = obj.children_li.split(",")
    
    
    if insert_at < 0: # append at the end
        
        # Prevent duplicate
        if str(target_child_id) in new_children_li:
            new_children_li.remove(str(target_child_id))
         
        new_children_li.append(str(target_child_id))
        print("------------APPENDED: {}".format(new_children_li))
        
    elif insert_at == 0: # no change

        # But it is possible a new object is created with order '0'
        # This should not happen, but just in case.
        if not str(target_child_id) in new_children_li:
            print("-----------no change, but this instance is new. Adding to Children_li")
            new_children_li.append(str(target_child_id))
            print("------------APPENDED: {}".format(new_children_li))
            
        print("-----------no change to children_li")
        
    else: # Insert at position
        
        # Prevent duplicate
        if str(target_child_id) in new_children_li:
            new_children_li.remove(str(target_child_id))
            
        print("-- Insert {} to position {}...".format(target_child_id, insert_at))
        print("------------BEFORE: {}".format(new_children_li))
        new_children_li.insert(int(insert_at-1), str(target_child_id)) 
        print("------------AFTER: {}".format(new_children_li))
 
    #turn it back to stringy list
    return ','.join(str(order) for order in new_children_li)
    

        
''' Removes an id out of the children_li '''
def remove_child(obj, target_child_id):
    
    new_children_li = []
    
    # if object's order_list is empty, 
    # it means it was never initialized or there is a problem
    if obj.children_li == "":
        new_children_li = refresh_children_li(obj) #Make new list by id
        new_children_li = new_children_li.split(",")
    else: 
        new_children_li = obj.children_li.split(",")
    
    print("-- Removing {}...".format(target_child_id))
    print("------------BEFORE: {}".format(new_children_li))
    
    # Check if id is already there. Then you have to swap
    if str(target_child_id) in new_children_li:
         new_children_li.remove(str(target_child_id))
    
    print("------------AFTER: {}".format(new_children_li))
    
    #turn it back to stringy list
    return ','.join(str(order) for order in new_children_li)






# -------------------------------------------
# -------------------------------------------
#           children_index helpers
# -------------------------------------------
# -------------------------------------------
# Note: experimental children_li vers.2. This list uses
#       index of children rather than their id directly. 
#       Pros: child id is never stored. 
#       Cons: harder to know which order the child is 
#             just by looking at the list.
#             Would need to query children to get the ids.  

# TODO: UPDATE THIS
''' Checks if children_li is valid '''
# Accepts children_li in form of stringy list or a list
def is_valid_children_index(cli):
    
    if isinstance(cli, str) or isinstance(cli, str): # is it a string?
        # note, 'unicode' was renamed to 'str' in Python 3
        cli = cli.split(",")
    elif isinstance(cli, list): # is it a list?
        pass
    else: 
        return False
        
    cli = ''.join(cli)
    cli = cli.replace(" ","")
    if cli == '' : return False
    
    return True
        


''' The children_order may be blank or invalid. 
Use this function refresh/recreate the order based on
the order the children appears in db'''

def refresh_children_index(obj):
    
    childrens = None
    if isinstance(obj, Strip):
        childrens = obj.frame_set.all()
    elif isinstance(obj, Scene):
        childrens = obj.strip_set.all()
    else:
        print("Not a valid object to extract children_index")
        return False
        
    # Make numerically ordered index list

    index_li = list(range(childrens.count())) 
    return ','.join(str(ind) for ind in index_li)



''' Updates children_li. This function most likely runs when save()
    Note: the insert_at number describes 'position', starts from 1.
          Make sure to -1 when using as an index, which starts from 0.
          
          '-1' = append at end
          '0' = no change in order'''

def update_children_index(obj, child_id, insert_at, is_new):

    # TODO: check if you need target_child_id at all?
    
    # because children_index is not id aware...you may need to you id

    new_children_index = []
    
    # if object's order_list is empty, 
    # it means it was never initialized or there is a problem
    if obj.children_index == "":
        new_children_index = refresh_children_index(obj) #Make new list by id
        new_children_index = new_children_index.split(",")
    else: 
        new_children_index = obj.children_li.split(",")
    
    # get target child's index. 
    # if it is new, it will simply be the last.

    target_c_index = len(new_children_index)


    if insert_at < 0: # append at the end
        
        # remove if already exists 
        if str(target_child_id) in new_children_li:
            new_children_li.remove(str(target_child_id))
         
        new_children_li.append(str(target_child_id))
        print("------------APPENDED: {}".format(new_children_li))
        
    elif insert_at == 0: # no change

        # But it is possible a new object is created with order '0'
        # This should not happen, but just in case.
        if not str(target_child_id) in new_children_li:
            print("-----------no change, but this instance is new. Adding to Children_li")
            new_children_li.append(str(target_child_id))
            print("------------APPENDED: {}".format(new_children_li))
            
        print("-----------no change to children_li")
        
    else: # Insert at position
        
        # Prevent duplicate
        if str(target_child_id) in new_children_li:
            new_children_li.remove(str(target_child_id))
            
        print("-- Insert {} to position {}...".format(target_child_id, insert_at))
        print("------------BEFORE: {}".format(new_children_li))
        new_children_li.insert(int(insert_at-1), str(target_child_id)) 
        print("------------AFTER: {}".format(new_children_li))
 
    #turn it back to stringy list
    return ','.join(str(order) for order in new_children_li)
    

        
''' Removes an id out of the children_li '''
def remove_child_index(obj, target_child_id):
    
    new_children_li = []
    
    # if object's order_list is empty, 
    # it means it was never initialized or there is a problem
    if obj.children_li == "":
        new_children_li = refresh_children_li(obj) #Make new list by id
        new_children_li = new_children_li.split(",")
    else: 
        new_children_li = obj.children_li.split(",")
    
    print("-- Removing {}...".format(target_child_id))
    print("------------BEFORE: {}".format(new_children_li))
    
    # Check if id is already there. Then you have to swap
    if str(target_child_id) in new_children_li:
         new_children_li.remove(str(target_child_id))
    
    print("------------AFTER: {}".format(new_children_li))
    
    #turn it back to stringy list
    return ','.join(str(order) for order in new_children_li)
