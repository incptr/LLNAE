import os, glob

class DeckViewer():
    def __init__(self,DeckSettings):
        self.deck_set = DeckSettings
        self.empty = True
        self.idx = 1
        self.n_cards = 0
        self.card_number = 1
        self.im_path =''
        
    def check_favorite(self):
        favorite = False
        
        with open(self.deck_set.path+'favorites.cfg') as f:
            lines = f.readlines()
            
        for line in lines:            
            vals = line.split(' ')
            indx = int(vals[0])
            if indx == self.idx:                
                favorite = int(vals[1])
        return favorite
        
    def save_favorite(self,fav_val):
        
        found = False
        with open(self.deck_set.path+'favorites.cfg') as f:
            lines = f.readlines()   
            
        for idx,line in enumerate(lines):
            vals = line.split(' ')
            card_indx = int(vals[0])
            
            if card_indx == self.idx:
                found = True
                vals[1] = str(fav_val)
                
                if fav_val == True:                
                    lines[idx] = '{} {} \n'.format(vals[0],1)
                else:
                    lines[idx] = ''
        
        with open(self.deck_set.path+'favorites.cfg','w') as f:
            f.writelines(lines)
            if found == False and fav_val == True:
                f.write('{} {} \n'.format(self.idx,1))
                
    def load_audio(self):
     
        start_idx = self.idx        
        self.audio_path = self.deck_set.path + 'audio/LLNa-{}-{}.wav'.format(self.deck_set.deck,start_idx)

        
        if os.path.isfile(self.audio_path):
            return self.audio_path
        else:
            return ''
        
    def load_picture(self,mode=''):
        
        start_idx = self.idx
        
        if mode == 'init':
            list_of_files = filter( os.path.isfile,
                          glob.glob(self.deck_set.path + 'images/' + '*') )
            list_of_files = sorted( list_of_files,
                                  key = os.path.getmtime)
            if len(list_of_files) > 0:
                start_idx = list_of_files[0]       
                start_idx = int(start_idx[19+2*len(self.deck_set.deck):-4])
                
        
   

        self.im_path = self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,start_idx)
        self.audio_path = self.deck_set.path + 'audio/LLNa-{}-{}.png'.format(self.deck_set.deck,start_idx)
        
        self.idx = max(start_idx,0) 
        idx = self.idx
        

        
        if os.path.isfile(self.im_path):
            return [self.im_path,idx]
        else:
            return ['',idx]
        
    def get_next_picture(self,direction=0,mode='standard',deletion=0):
        
        # loop around 0->-1 
        
        # get first and last index
        list_of_files = filter( os.path.isfile,
                      glob.glob(self.deck_set.path + 'images/' + '*') )
        list_of_files = sorted( list_of_files,
                              key = os.path.getmtime)
        
        if len(list_of_files) == 0:
            return['','','',self.idx]

        first_index = list_of_files[0]     
        first_index = int(first_index[19+2*len(self.deck_set.deck):-4])
        
        last_index = list_of_files[-1]
        last_index = int(last_index[19+2*len(self.deck_set.deck):-4])

        
        start_idx = self.idx
        img_found = False
        
        while not img_found:
            
            if start_idx <= first_index and direction == -1:
                start_idx = last_index
                self.im_path = self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.audio_path = self.deck_set.path + 'audio/LLNa-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.card_number = self.n_cards
                break
            
            elif start_idx >= last_index and direction == 1:
                start_idx = first_index
                self.im_path = self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.audio_path = self.deck_set.path + 'audio/LLNa-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.card_number = 1
                break
            
            start_idx = start_idx+direction
            self.im_path = self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,start_idx)
            self.audio_path = self.deck_set.path + 'audio/LLNa-{}-{}.png'.format(self.deck_set.deck,start_idx)
            
            if os.path.isfile(self.im_path):
                img_found = True
                self.card_number = self.card_number + direction - deletion
        
        self.idx = start_idx

        if os.path.isfile(self.im_path):
            return [self.im_path,self.idx]
        else:
            return ['',self.idx]
        
