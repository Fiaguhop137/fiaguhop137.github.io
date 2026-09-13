import importlib.util
import subprocess
import sys
for package in ['pyautogui','pyperclip','selenium','pygetwindow']:
    if importlib.util.find_spec(package) is None:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
import pyautogui
import pygetwindow
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
catNames=[]
catLinks=[]
run=False
while not run:
    cats=int(input('How many tests? '))
    speed=str((cats*6)//60)+' minutes and '+str(cats*6-((cats*6)//60)*60)+ ' seconds'
    run='y' in input(f'This will take a minimum of {speed}. Proceed? ').strip().lower()
options=Options()
options.add_argument('--headless=new')
driver=webdriver.Chrome(options=options)
pyautogui.hotkey('win','r')
pyautogui.typewrite('chrome')
pyautogui.press('enter')
while not any('Chrome' in window for window in pygetwindow.getAllTitles()):
    time.sleep(0.1)
chrome_window = None
while not chrome_window:
    for w in pygetwindow.getAllWindows():
        if 'Chrome' in w.title:
            chrome_window = w
            break
    time.sleep(0.1)
chrome_window.activate()
pyautogui.press('tab')
pyautogui.press('enter')
shopFails=0
while len(catNames)<cats:
    link='https://tabbycats.club/shop'
    pyautogui.hotkey('ctrl','t')
    time.sleep(1)
    pyautogui.click(1880,160)
    while link=='https://tabbycats.club/shop':  
        time.sleep(0.5)
        pyautogui.hotkey('tab')
        pyautogui.hotkey('enter')
        time.sleep(1)
        pyautogui.hotkey('ctrl','l')
        pyautogui.hotkey('ctrl','c')
        link=pyperclip.paste()
        pyautogui.hotkey('ctrl','w')
    driver.get(link)
    try:
        catNameList=driver.find_element(By.CLASS_NAME,'pet-name').text.strip().split()
    except:
        catNameList=['Shop','Fail']
        shopFails+=1
    catName=' '.join(name.capitalize() for name in catNameList)
    if not catName=='Shop Fail':
        catNames.append(catName)
        catLinks.append(link)
    pyautogui.hotkey('ctrl','w')
driver.quit()
pyautogui.hotkey('alt','tab')
legends=['Fiery', 'Evil', 'Pinky', 'Space', 'Night', 'Rainbow', 'Tiny']
legendcats=[]
legendlinks=[]
for x in range(cats):
    print(f'Cat {x+1}: \n └> Name: {catNames[x]}. \n └> Link: {catLinks[x]}.')
    if any(name in catNames[x] for name in legends) and 'Nightmare' not in catNames[x]:
        legendcats.append(catNames[x])
        legendlinks.append(catLinks[x])
for x in range(len(legendcats)):
    print(f'Legendary Cat {x+1}: \n └> Name: {legendcats[x]}. \n └> Link: {legendlinks[x]}.')
shopFailPercent=round(shopFails/((cats+shopFails))*100, 2)
print(f'It failed and went to shop instead {shopFails} times, or {shopFailPercent}% of the time.')