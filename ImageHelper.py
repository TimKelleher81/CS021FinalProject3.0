import os
from PIL import Image
import AlarmTime
from sys import platform

# Current image_path being used:
# C:\Users\Tim\Desktop\Meme_Acct_BS\11_28_18_meme_queue\
# Current old_images_path being used:
# C:\Users\Tim\Desktop\Meme_Acct_BS\replaced\
MAXFILESIZE = 8000000
MAXRATIO = 1.7777
MINRATIO = 0.8
# The two following values are the max resolutions that Instagram will store on their servers
MAXWIDTH = 1080
MAXHEIGHT = 1350
image_data = {}
other_data = {'invalidCount': 0, 'totalImgErrors': 0}
data_found = False
rollover_data = []
do_rollover = True
image_path = ''
old_images_path = ''
new_image_pre = 'EDIT-'  # Prefix attached to the new image when one is edited and replaced
separator = ''


def main():
    global image_data, data_found, other_data, rollover_data, image_path, separator

    if platform == "darwin":
        separator = '/'
    elif platform == "win32":
        separator = '\\'

    get_rollover()

    check_file_paths()

    print('Timeout is currently set to', str(AlarmTime.timeout), 'seconds.')

    while True:
        main_menu()

        safe_input('\nPress enter to continue...\n\n')


# Runs main menu options based on user input given by function 'main_menu_options()'
def main_menu():
    options = main_menu_options()

    if options == 1:
        view_all_images()
    elif options == 2:
        list_invalid()
    elif options == 3:
        for i in range(1, len(image_data) + 1):
            print_img_details(img_key_get(i))
    elif options == 4:
        print('Updating image data.')
        update_image_data()
        print('Finished')
    elif options == 5:
        settings_menu()
    elif str(options).lower() == 'e':
        print('Closing program.')
        update_rollover()
        return
    else:
        print('Option does not exist.')


# Prints main menu and receives user input. Then validates that input.
def main_menu_options():

    # 0 should never be used as an option,
    # as that is what is used when an invalid string is received.
    print('\n\n' + 'Options Menu:')
    print('----------------------------------------------')
    print('     View images and data ------------------ 1')
    print('\t\t- ' + str(len(image_data)) + ' image(s) found -')
    print('     List images found with errors --------- 2')
    if other_data['invalidCount'] > 0:
        print('\t\t- ' + str(other_data['invalidCount']) + ' image(s) - '
              + str(other_data['totalImgErrors']) + ' total error(s) -')
    else:
        print('\t\t- 0 image errors -')
    print('     Display all image data ---------------- 3')
    print('\t\t- ' + str(len(image_data['1'])) + ' elements per image -')
    print('     Update image data --------------------- 4')
    print('     Settings ------------------------------ 5')
    print('     End program --------------------------- E')

    user_select = safe_input('Selection: ')
    print('\n')

    try:
        user_select = int(user_select)
    except ValueError:
        if user_select.lower() != 'e':
            user_select = 0
    return user_select


# Runs settings menu options based on user input given by function 'settings_menu_options()'
def settings_menu():
    global image_path
    while True:

        options = settings_menu_options()

        if options == 1:
            AlarmTime.update_timeout_u()
        elif options == 2:
            file_path_change_options()
        elif options == 3:
            user_select = safe_input('Save settings between sessions? (y/n) ')
            if user_select.lower() == 'y':
                rollover_data[2][2] = 'True'
                print('Enabled')
            elif user_select.lower() == 'n':
                rollover_data[2][2] = 'False'
                print('Disabled')
            else:
                print('Invalid input')
        elif options == 4:
            user_update_prefix()
        elif options == 5:
            rollover_data[0][2] = ' '
            rollover_data[1][2] = AlarmTime.DEFAULT
            rollover_data[2][2] = 'True'
            rollover_data[3][2] = ' '
            rollover_data[4][2] = 'EDIT-'
            update_from_rollover()
            update_rollover()
            print('All settings reset to default.')
        elif str(options).lower() == 'e':
            return
        else:
            print('Option does not exist.')
        safe_input('\nPress enter to continue...\n\n')


# Prints settings menu and receives user input. Then validates that input.
# Should be run as an option off of main menu
def settings_menu_options():

    print('\n\n' + 'Settings Menu:')
    print('----------------------------------------------')
    print('     Change timeout length ----------------- 1')
    print('     Change file paths --------------------- 2')
    print('     Enable/Disable data rollover ---------- 3')
    print('     Change new image prefix --------------- 4')
    print('     Reset settings ------------------------ 5')
    print('     Return to main menu ------------------- E')

    user_select = safe_input('Selection: ')
    print('\n')

    try:
        user_select = int(user_select)
    except ValueError:
        if user_select.lower() != 'e':
            user_select = 0
    return user_select


# Either cycles through images 1 by 1 or lists all.
# At end, allows user to select and image to view more options on.
# If cycling through, allows user to select the current image to view more options
#   in the same way that is available at the end.
def view_all_images():

    cycle = safe_input("\nEnter 0 to cycle through all images\n"
                       "\tor enter 1 to list all with the option to select at the end: ")
    try:
        cycle = int(cycle)
    except ValueError:
        cycle = ''
    # Used in case that image_data is changed within, so that the length of the loop can still be referred to
    length = len(image_data) + 1
    i = 1
    loop = True
    menu = False

    if cycle == 0:
        print("\nEnter 0 to select the current image, \n"
              "\tenter an image number or its title to select that image,\n"
              "\tor press enter to continue to the next image: ")
    elif cycle == 1:
        print("\nListing images:\n")
    else:
        loop = False
        menu = True
        print('Invalid input, returning to menu.')
    while loop:
        try:
            print('\n' + str(i) + '- ' + image_data[str(i)]['fileName'])

            if cycle == 0:
                cont = safe_input("\n")
                if cont != '':
                    cont = img_key_get(cont)

                    if cont == '0':
                        image_menu(str(i))
                    elif cont > '0':
                        image_menu(cont)

                    cycle = safe_input("\nPress enter to return to the main menu,\n"
                                       "\tenter 0 to continue cycling through images, \n"
                                       "\tor enter 1 to list all images from start: ")
                    try:
                        cycle = int(cycle)
                    except ValueError:
                        cycle = ''
                    if cycle == 0:
                        print("\nEnter 0 to select the current image, \n"
                              "\tenter an image number or its title to select that image,\n"
                              "\tor press enter to continue to the next image: ")
                    elif cycle == 1:
                        print("\nListing images:\n")
                        i = 1
                else:
                    i += 1
            elif cycle == 1:
                i += 1
            else:
                loop = False
                menu = True
        except KeyError:
            i = length

        if i >= length and (menu is False):
            i, length, loop = view_images_loop_check(i, length)


# Used at the conclusion of view all images essentially to ask the user
#   if they would like to run the loop again
def view_images_loop_check(i, length):
    user_select = ' '
    while user_select != '':
        user_select = safe_input("\nEnter an image's name or the number to the left of it to view its options."
                                 "\nOtherwise, press enter to continue: ")
        if user_select != '':
            image_menu(img_key_get(user_select))

    print('Would you like to have the image list displayed again? Press enter for no, or:')
    cycle = safe_input("\n\tEnter 0 to cycle through all images\n"
                       "\tor enter 1 to list all with the option to select at the end: ")
    try:
        cycle = int(cycle)
        length = len(image_data) + 1
        i = 1
        loop = True
    except ValueError:
        cycle = ''
        loop = False

    if cycle == 0:
        print("\nEnter 0 to select the current image, \n"
              "\tenter an image number or its title to select that image,\n"
              "\tor press enter to continue to the next image: ")
    elif cycle == 1:
        print("\nListing images:\n")
    else:
        loop = False
        print('Invalid input, returning to menu.')

    return i, length, loop


# Runs settings menu options based on user input given by function 'image_menu_options()'
# Parameter i should be the key for the image selected
def image_menu(image_key):
    global image_path
    i = image_key
    loop = True
    while loop:

        options = image_menu_options(i)

        if options == 1:
            print_img_details(i)
        elif options == 2:
            img = Image.open(image_data[i]['path'])
            img.show()
        elif options == 3:
            change_image_name(i)
        elif str(options).lower() == 'e':
            loop = False
        else:
            print('Option does not exist.')
        safe_input('\nPress enter to continue...\n\n')
    update_image_data()


# Prints image menu and receives user input. Then validates that input.
# Should be run as an option off of view_all_images()
def image_menu_options(i):

    print('\n\n' + 'Image Options Menu: ' + str(i) + '- ' + image_data[i]['fileName'])
    print('----------------------------------------------')
    print('     Display details ----------------------- 1')
    print('     View image ---------------------------- 2')
    print('     Change image name --------------------- 3')
    print('     Return -------------------------------- E')

    user_select = safe_input('Selection: ')
    print('\n')

    try:
        user_select = int(user_select)
    except ValueError:
        if user_select.lower() != 'e':
            user_select = 0
    return user_select


# Changes image_path based upon user input. Then validates that the path exists.
# (The main path (image_path) is where the program will look for images to give information on, edit, and post.)
# Note: The program currently cannot post at all. In the future, it may be able upload to Buffer.com
#   however, besides that Instagram does not allow any automated posting (I believe)
def change_main_path():
    global image_path
    path = old_images_path
    if old_images_path:
        print('The current main file path is:')
        print('\t' + image_path)
        path = safe_input('This will be where the program will look for images '
                          'to give information on, edit, and post.\n'
                          'Please enter a new main file path for images. '
                          'Or press enter to maintain the current path.\n')

        if os.path.exists(image_path) and path == '':
            return
    while (not os.path.exists(path)) or path is False:
        print('\tPath given or current path does not exist.')
        path = safe_input('\tPlease enter a new main file path for images: ')

    if path[-1] != separator:
        path += separator

    image_path = path


# Changes old_images_path (the path that old copies of edited or removed images are stored in)
#   based upon user input. Then validates that the path exists.
def change_old_images_path():
    global old_images_path
    path = old_images_path
    if old_images_path:
        print('The current old images file path is:')
        print('\t' + old_images_path)
        path = safe_input('This will be where the program puts old copies of edited or removed images.\n'
                          'Please enter a new old images file path. Or press enter to maintain the current path.\n')

        if os.path.exists(old_images_path) and path == '':
            return
    while (not os.path.exists(path)) or path is False:
        print('\tPath given or current path does not exist.')
        path = safe_input('\tPlease enter a new old images file path: ')

    if path[-1] != separator:
        path += separator

    old_images_path = path


# Should be triggered through settings menu.
# Used to get the user's choice on whether they wish to change the main file path or old images file path.
#   If main file path is selected, update_image_data() function is called afterwards.
# Only the above two options are valid
def file_path_change_options():
    user_select = safe_input('Change main file path or old images file path?\n'
                             'Enter 1 for main or 2 for old.\n ')
    if user_select.lower() == '1':
        change_main_path()
        print('\n\tUpdating image data.')
        update_image_data()
        print('\tFinished.\n')
    elif user_select.lower() == '2':
        change_old_images_path()
    else:
        print('Invalid input')


# Collects and formats image data and adds to image_data dictionary.
# Key for each image is simply a number (could be changed in the future)
def update_image_data():
    global image_data, image_path
    image_data.clear()
    image_names = os.listdir(image_path)

    count = 1
    for image_name in image_names:
        if image_name != '.DS_Store':
            title = str(count)
            image_data.update({title: {'fileName': image_name}})
            image_data[title].update({"path": image_path + image_name})
            info = os.stat(image_data[title]["path"])
            image_data[title].update({"size": info.st_size})
            image_data[title].update({"timeOfLastAccess": info.st_mtime})
            ext = image_name.split('.')[-1]
            ext = str('.' + str(ext).lower())
            image_data[title].update({"extension": ext})
            image_data[title]["extension"].upper()
            img = Image.open(image_data[title]["path"])
            image_data[title].update({"width": ''})
            image_data[title].update({"height": ''})
            image_data[title]["width"], image_data[title]["height"] = img.size
            image_data[title].update({"ratio": image_data[title]["width"] / image_data[title]["height"]})

            update_image_validity_data(title)

            count += 1
    update_invalid_count()


# Generates remaining image data that stems from Instagram requirements as conditional statements
def update_image_validity_data(title):
    global image_data
    other_data['totalImgErrors'] = 0

    if image_data[title]["size"] <= MAXFILESIZE:
        image_data[title].update({"validSize": True})
    else:
        image_data[title].update({"validSize": False})
        other_data['totalImgErrors'] += 1

    if image_data[title]["extension"] == '.jpg' or image_data[title]["extension"] == '.jpeg' \
            or image_data[title]["extension"] == '.png':
        image_data[title].update({"validExtension": True})
    else:
        image_data[title].update({"validExtension": False})
        other_data['totalImgErrors'] += 1

    if MAXRATIO > image_data[title]["ratio"] > MINRATIO:
        image_data[title].update({"validRatio": True})
    else:
        image_data[title].update({"validRatio": False})
        other_data['totalImgErrors'] += 1

    if image_data[title]["ratio"] > 1:
        image_data[title].update({"ratioType": 'landscape'})
    elif image_data[title]["ratio"] < 1:
        image_data[title].update({"ratioType": 'portrait'})
    else:
        image_data[title].update({"ratioType": 'square'})

    if image_data[title]["width"] < MAXWIDTH:
        image_data[title].update({"validHorizontalResolution": True})
    else:
        image_data[title].update({"validHorizontalResolution": False})

    if image_data[title]["height"] < MAXHEIGHT:
        image_data[title].update({"validVerticalResolution": True})
    else:
        image_data[title].update({"validVerticalResolution": False})


# Edits a given invalid image to fit within the Instagram ratio requirements.
# Adds equally sized white bars to either the top and bottom or left and right of an image.
# Size of white bars will make the new image ratio the minimum required depending on landscape or portrait.
# Moves old image to old_images_path while new image is placed in image_path
#   and has the 'new_image_pre' prefix added to the front.
# Calls the 'update_image_data()' function after
def fix_ratio(i):
    global image_path
    if image_data[i]['validRatio']:
        return
    if image_data[i]['ratioType'] == 'landscape':
        goal_height = int(image_data[i]['width'] / MAXRATIO) + 1
        delta_height = int((goal_height - image_data[i]['height']) / 2) + 1
        imgw = Image.new('RGB', (image_data[i]['width'], delta_height), color='white')
        new_img = Image.new('RGB', (image_data[i]['width'], goal_height))
        y_offset = 0
        new_img.paste(imgw, (0, y_offset))
        y_offset += imgw.size[1]
        img = Image.open(image_data[i]['path'])
        new_img.paste(img, (0, y_offset))
        y_offset += img.size[1]
        new_img.paste(imgw, (0, y_offset))
    else:  # portrait
        goal_width = int(image_data[i]['height'] / MINRATIO) + 1
        delta_width = int((goal_width - image_data[i]['width']) / 2) + 1
        imgw = Image.new('RGB', (delta_width, image_data[i]['height']), color='white')
        new_img = Image.new('RGB', (goal_width, image_data[i]['height']))
        x_offset = 0
        new_img.paste(imgw, (x_offset, 0))
        x_offset += imgw.size[0]
        img = Image.open(image_data[i]['path'])
        new_img.paste(img, (x_offset, 0))
        x_offset += img.size[0]
        new_img.paste(imgw, (x_offset, 0))

    new_img.save(image_data[i]['fileName'])
    print('Old image will be moved to: ' + old_images_path)
    os.rename(image_path + image_data[i]['fileName'], old_images_path + image_data[i]['fileName'])
    print('New image will be saved in: ' + image_path)
    print('\twith the file name: ' + new_image_pre + image_data[i]['fileName'])
    f = new_image_pre + image_data[i]['fileName']
    os.rename(os.path.dirname(os.path.abspath(__file__)) + separator + image_data[i]['fileName'], image_path + f)
    update_image_data()
    for num in image_data:
        if image_data[num]['fileName'] == f:
            print(image_data[num]['fileName'] + ' now has a valid ratio:')
            print('\tRatio Type: ' + image_data[num]['ratioType'])
            print('\tWidth (px): ' + str(image_data[num]['width']))
            print('\tHeight (px): ' + str(image_data[num]['height']))
            print('\tRatio: 1:' + format(image_data[num]['ratio'], '.2f'))


# Copies data from 'rollover_data.txt' into the rollover_data array.
# Sets 'data_found' to true if data is present within the file and vice versa
# Creates the text file if it does not exist
def get_rollover():
    global data_found, rollover_data, image_path, do_rollover, old_images_path, new_image_pre
    try:
        rollover_data_fh = open('rollover_data.txt', 'r')
        rollover_data = rollover_data_fh.readlines()
        if rollover_data:
            data_found = True
        else:
            data_found = False

    except FileNotFoundError:
        rollover_data_fh = open('rollover_data.txt', 'w')
    rollover_data_fh.close()
    if data_found:
        for i in range(len(rollover_data)):
            rollover_data[i] = rollover_data[i].rstrip()
            rollover_data[i] = rollover_data[i].split()
        update_from_rollover()


# Updates rollover_data array with the values from the more specific variables if do_rollover and data_found = True
# Then writes data to 'rollover_data.txt'
# If do_rollover = True and data_found = False, provides the labels for the data within 'rollover_data.txt'
#   and should use the same more specific values as above.
#   In this case, they would likely be the same values they are initialized with at the top.
# If do_rollover = False and data_found = False, writes the last data contained within
#   the rollover_data array to 'rollover_data.txt'
def update_rollover():
    if do_rollover:
        if data_found:
            for i in range(len(rollover_data)):
                rollover_data[i][1] = '='
            rollover_data[0][-1] = image_path
            rollover_data[1][-1] = str(AlarmTime.timeout)
            rollover_data[3][-1] = old_images_path
            rollover_data[4][-1] = new_image_pre

            rollover_data_fh = open('rollover_data.txt', 'w')
            for i in range(len(rollover_data)):
                try:
                    rollover_data_fh.write(rollover_data[i][0] + ' = ' + str(rollover_data[i][2]) + '\n')
                except IndexError:
                    rollover_data[i][1] = '='
                    rollover_data[i].append(' ')
                    rollover_data_fh.write(rollover_data[i][0] + ' = ' + rollover_data[i][2] + '\n')
        else:
            rollover_data_fh = open('rollover_data.txt', 'w')
            rollover_data_fh.write('image_path = ' + image_path + '\n')
            rollover_data_fh.write('timeout = ' + str(AlarmTime.timeout) + '\n')
            rollover_data_fh.write('settingsRollover = True\n')
            rollover_data_fh.write('old_images_path = ' + old_images_path + '\n')
            rollover_data_fh.write('new_image_pre = EDIT-')
        rollover_data_fh.close()
    else:
        rollover_data_fh = open('rollover_data.txt', 'w')
        rollover_data_fh.write('image_path = ' + rollover_data[0][-1].strip() + '\n')
        rollover_data_fh.write('timeout = ' + rollover_data[1][-1].strip() + '\n')
        rollover_data_fh.write('settingsRollover = False\n')
        rollover_data_fh.write('old_images_path = ' + rollover_data[3][-1].strip() + '\n')
        rollover_data_fh.write('new_image_pre = ' + rollover_data[4][-1].strip())
    rollover_data_fh.close()


# Similar to update_rollover() function but in reverse.
# Do rollover is updated through the rollover_data array first
# If do_rollover = True, does the opposite of update_rollover()
# If do_rollover = False, sets both path variables to nothing or a blank string
# After doing the above, checks if each path exists, and if not sets that one = to False
#   This is used to force the user to provide a new path if the existing one does not exist
def update_from_rollover():
    global image_path, do_rollover, old_images_path, new_image_pre
    do_rollover = bool(rollover_data[2][2])
    if do_rollover:
        image_path = rollover_data[0][-1].strip()
        AlarmTime.update_timeout(int(str(rollover_data[1][-1]).strip()))
        old_images_path = rollover_data[3][-1].strip()
        new_image_pre = rollover_data[4][-1].strip()
    else:
        # Not sure why I have it doing this
        # Could be that I don't want it to save any file paths if rollover is off
        image_path = ''
        old_images_path = ''
    if not os.path.exists(image_path):
        image_path = False
    if not os.path.exists(old_images_path):
        old_images_path = False


# Lists each image with some form of error.
# In the case of an invalid ratio prompts the user
#   if they would like it edited to fix the ratio, if so runs 'fix_ratio()'
def list_invalid():
    global other_data
    if other_data['invalidCount'] > 0:
        count = 1
        for i in image_data:
            if not image_data[i]['validRatio']:
                print(str(count) + ' - ' + image_data[i]['fileName'] + ' has an invalid ratio:')
                print('\tRatio Type: ' + image_data[i]['ratioType'])
                print('\tWidth (px): ' + str(image_data[i]['width']))
                print('\tHeight (px): ' + str(image_data[i]['height']))
                print('\tRatio: 1:' + format(image_data[i]['ratio'], '.2f'))
                user_select = safe_input(
                    "\nPress enter to pass the image "
                    "or enter F to have it edited to a valid ratio with no content lost: ")
                if user_select.lower() == 'f':
                    fix_ratio(i)
                else:
                    count += 1

            if not image_data[i]['validSize']:
                print(str(count) + ' - ' + image_data[i]['fileName'] + ' has an invalid size: \n\tover '
                      + str(MAXFILESIZE / 1000000) + 'MB')
                count += 1

            if not image_data[i]['validExtension']:
                print(str(count) + ' - ' + image_data[i]['fileName'] + ' has an invalid file extension: \n\t'
                      + image_data[i]["extension"])
                count += 1
        other_data['totalImgErrors'] = count
    else:
        print('No current image errors. Returning to menu.')


# Creates a count of images that have at least one invalid element
def update_invalid_count():
    other_data['invalidCount'] = 0
    for i in image_data:
        if image_data[i]['validSize'] is False or image_data[i]['validRatio'] is False \
                or image_data[i]['validExtension'] is False:
            other_data['invalidCount'] += 1


# Accepts either the number key for the image_data array or an image title.
# Validates that they correspond to an actual image, then returns the key
def img_key_get(location):
    try:
        try:
            location = int(location)
            return str(location)
        except ValueError:
            for i in image_data:
                if image_data[i]['fileName'] == location:
                    return i
    except KeyError:
        print('The image requested does not exist.')
        try:
            return ''
        except KeyError:
            return


# Prints all data for and image based upon it's key within the image_data
# Also includes some special formatting cases
def print_img_details(num: str):
    print(num + ': ' + image_data[num]['fileName'].split('.')[0])
    print((len(image_data[num]['fileName']) + 4) * '-')
    for i in image_data[num]:
        if i == 'size':
            print(i + ' (bytes)' + ((15 - len(i)) * '-') + ' ' + str(image_data[num][i]))
        elif i == 'width' or i == 'height':
            print(i + ' (px)' + ((18 - len(i)) * '-') + ' ' + str(image_data[num][i]))
        elif i == 'ratio':
            print(i + ' (width/height)' + ((8 - len(i)) * '-') + ' ' + format(image_data[num][i], '.2f'))
        else:
            print(i + ' ' + ((22 - len(i)) * '-') + ' ' + str(image_data[num][i]))


# Used in place of 'input()' in order to use a timeout in every request for input,
#   as well as updating the rollover text file beforehand in order to avoid losing data if the program is closed.
def safe_input(prompt: str):
    AlarmTime.start()
    update_rollover()
    s = input(prompt)
    AlarmTime.kill()
    return s


# Checks if each file path has had a value set, if not or if it is set to False then
#   runs either 'change_main_path()' or 'change_old_images_path()' depending which path.
# Then runs 'update_image_data() afterwards'
def check_file_paths():
    if image_path:
        print('Previous main file path has been found:')
        print('\t' + image_path)
    else:
        print('The pre-existing main file path does not exist or is invalid.')
        change_main_path()

    if old_images_path:
        print('Previous old images file path has been found:')
        print('\t' + image_path)
    else:
        print('The pre-existing old images file path does not exist or is invalid.')
        change_old_images_path()

    print('\n\tUpdating image data.')
    update_image_data()
    print('\tFinished\n')


# Updates the prefix added to the beginning of the image title based on user input
def user_update_prefix():
    global new_image_pre
    user_select = safe_input("The current new image prefix attached to a new image when one is edited and replaced is '"
                             + new_image_pre + "'\nPress enter to keep the current prefix, or enter a new one: ")
    if user_select.lower() != '':
        new_image_pre = user_select


def change_image_name(image_key):
    name = image_data[image_key]['fileName'].split('.')
    print('Current name is: ' + name[0])
    new_name = safe_input('Enter a new name to replace it or enter to cancel the change: ')
    if new_name != '':
        os.rename(image_path + image_data[image_key]['fileName'], image_path + new_name + '.' + name[-1])
        image_data.update({image_key: {'fileName': new_name + '.' + name[-1]}})
        image_data[image_key].update({"path": image_path + new_name + '.' + name[-1]})
        print('Saved.')


main()
