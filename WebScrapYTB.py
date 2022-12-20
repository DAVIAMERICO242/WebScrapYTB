from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import undetected_chromedriver.v2 as uc##para nao ter problemas de login excessivo
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC

class ytb_your_data:
    def __init__(self,login,password,n_rolls=None):#n_roll: o tanto de roladas ate o final da pagina inicial do youtube
        self.login=login
        self.password=password
        self.n_rolls=n_rolls
    def ytb_scrap(self,sleep0=2):#sleep0: tempo estimado pelo usuário para carregar os videos posteriores apos um scroll down completo
        options=uc.ChromeOptions()
        options.add_argument('start-maximized')
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        driver=uc.Chrome(options=options)
        driver.delete_all_cookies()
        driver.get('https://www.youtube.com/')#pagina desejada
        try:
           WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='buttons']/ytd-button-renderer")))#aguardar o botao de login ser achado
        except:
           print('waiting too much')
        login_button=driver.find_element(By.XPATH,"//div[@id='buttons']/ytd-button-renderer")#clicando no botao de login
        login_button.click()
        try:
           WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='identifierId']")))#aguardar ate achar a caixa de login
        except:
           print('waiting too much')
        login_box=driver.find_element(By.XPATH,"//input[@id='identifierId']")
        login_box.send_keys(self.login)#enviar o login para caixa de login
        login_next_button=driver.find_element(By.XPATH,"//div[@id='identifierNext']//button")
        login_next_button.click()#clicar para ir procurar a senha
        try:
           WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='password']//input[@class='whsOnd zHQkBf']")))#aguardar a caixa de senha ser visivel
        except:
           print('waiting too much')
        sleep(1)
        pass_box=driver.find_element(By.XPATH,"//div[@id='password']//input[@class='whsOnd zHQkBf']")
        pass_box.click()
        pass_box.send_keys(self.password)#escrever a senha
        pass_next_button=driver.find_element(By.XPATH,"//div[@id='passwordNext']//button")
        pass_next_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='meta' and @class='style-scope ytd-rich-grid-media']")))
        if self.n_rolls is None:#se é None rolamos ate o final da pagina
            last_height = driver.execute_script("return document.documentElement.scrollHeight")#tamanho da barra de scroll antes do rolamento
            while True: 
               driver.execute_script('window.scrollTo(0,document.documentElement.scrollHeight);')#rolar ate o final da pagina e atualizar
               sleep(sleep0)
               new_height=driver.execute_script("return document.documentElement.scrollHeight")#tamanho da barra de scroll apos o rolamento
               if new_height == last_height:#se o tamanho da barra de scroll continua a mesma entao a pagina acabou
                 break
               last_height = new_height
        else:
            for k in range(self.n_rolls()):
                driver.execute_script('window.scrollTo(0,document.documentElement.scrollHeight);')
                sleep(self.sleep)
        source=driver.page_source#pegar o codigo fonte da casa
        driver.close()
        soup=BeautifulSoup(source,'html.parser')#passando pelo soup
        video_box=soup.find_all('div',{'id':'meta','class':'style-scope ytd-rich-grid-media'})#pegando o codigo fonte que armazena as informações dos videos particulares
        video_title=[]
        channel_name=[]
        video_views=[]
        posted_at=[]
        verified=[]
        for i in range(len(video_box)):
            a=video_box[i].find('yt-formatted-string',{'id':'video-title'})#procurando titulo do video
            if(a.text[0:3]=='Mix' or a.text=="Meu mix"):#nao iremos pegar os mix
                continue
            b=video_box[i].find('ytd-channel-name',{'id':'channel-name'}).find('a',{'class':'yt-simple-endpoint style-scope yt-formatted-string'})#nome do canal
            c=video_box[i].find('div',{'id':'metadata-line'}).find_all('span',{'class':'inline-metadata-item style-scope ytd-video-meta-block'})
            if len(c)==2:#as regras para saber se um video é live e etc foram criadas estudando o codigo html
               video_title.append(a.text)
               channel_name.append(b.text)
               video_views.append(c[0].text)
               posted_at.append(c[1].text)
            else:
               video_title.append(a.text)
               channel_name.append(b.text)
               video_views.append(c[0].text)
               if video_box[i].contents[2].div.span.text=="AO VIVO":
                  posted_at.append('LIVE')        
               else:
                  posted_at.append('PREMIERE')
            if video_box[i].find('ytd-channel-name',{'id':'channel-name'}).find('path',{'class':'style-scope yt-icon','d':'M12,2C6.5,2,2,6.5,2,12c0,5.5,4.5,10,10,10s10-4.5,10-10C22,6.5,17.5,2,12,2z M9.8,17.3l-4.2-4.1L7,11.8l2.8,2.7L17,7.4 l1.4,1.4L9.8,17.3z'}) is not None:
                  verified.append('Yes')  
            else:
                  verified.append('No')
        dic={'Video title':video_title,'Channel name':channel_name,'Video views':video_views,'Posted at':posted_at,'Verified':verified}
        data=pd.DataFrame(dic)
        return data
        








