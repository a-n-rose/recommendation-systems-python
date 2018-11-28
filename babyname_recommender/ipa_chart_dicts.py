'''
IPA collected using Espeak

Used IPA chart (and Wikipedia for 'w') to categorize all ipa characters
in the US American names used in Social Security Applications from 1880 to 2017.

These characters probably cover all US American English IPA characters
'''

def ipa_characters():
    chars = ('a', 'b', 'd', 'e', 'f', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'z', 'æ', 'ð', 'ø', 'ŋ', 'ɐ', 'ɑ', 'ɔ', 'ə', 'ɚ', 'ɛ', 'ɜ', 'ɡ', 'ɣ', 'ɪ', 'ɬ', 'ɹ', 'ɾ', 'ʃ', 'ʊ', 'ʌ', 'ʒ', 'ʔ', 'ˈ', 'ˌ', 'ː', '̩', 'θ', 'ᵻ')
    return chars

def ipa_vowels():
    vowels = []
    vowel_types = ipa_vowels_dict()
    for key, value in vowel_types.items():
        vowels.append(list(value))
    vowels = sorted(set([item for sublist in vowels for item in sublist]))
    return vowels

def ipa_vowels_dict():
    ipa_vowels = {}
    ipa_vowels["open_vowels"] =('æ','ɐ','a','ɑ')
    ipa_vowels["mid_vowels"]  = ('e','o','ø','ɔ','ə','ɚ','ɛ','ɜ','ʌ')
    ipa_vowels["close_vowels"] = ('i','u','ɪ','ʊ','ᵻ')

    ipa_vowels["front_vowels"] = ('i','ɪ','e','ø','ɛ','æ','a')
    ipa_vowels["central_vowels"] = ('ᵻ','ə','ɜ','ɐ',)
    ipa_vowels["back_vowels"] = ('u','ʊ','o','ʌ','ɔ','ɑ',)

    ipa_vowels["rounded_vowels"] = ('u','o','ɔ')
    
    return ipa_vowels

def ipa_consonants_dict():
    #categorized 'w' as labio-velar approximant based on wikipedia 
    #https://en.wikipedia.org/wiki/Voiced_labio-velar_approximant
    ipa_consonants = {}
    ipa_consonants["voiced"] = ("b","m","v","ð","d","n","r","ɾ","z","ʒ","ɹ","l","j","ɡ","ŋ","ɣ","w")
    
    ipa_consonants["voiceless"] = ("p","f","θ","t","s","ɬ","k","x","ʔ","h")
    
    ipa_consonants["plosive"] = ("p","b","t","d","k","ɡ","ʔ")
    
    ipa_consonants["nasal"] = ("m","n","ŋ")
    ipa_consonants["tril"] = ("r")
    ipa_consonants["tap"] = ("ɾ")
    ipa_consonants["fricative"] = ("f","v","θ","ð","s","z","ʃ","ʒ","x","ɣ","h")
    ipa_consonants["lateral_fricative"] = ("ɬ")
    ipa_consonants["approximant"] = ("ɹ","j","w")
    ipa_consonants["lateral_approximant"] = ("l")
    
    ipa_consonants["bilabial"] = ("b","m")
    ipa_consonants["labiodental"] = ("f","v")
    ipa_consonants["labiovelar"] = ("w")
    ipa_consonants["dental"] = ("θ","ð")
    ipa_consonants["alveolar"] = ("t","d","n","r","ɾ","s","z","ɬ","ɹ","l")
    ipa_consonants["postalveolar"] = ("ʃ","ʒ")
    ipa_consonants["retroflex"] = ()
    ipa_consonants["palatal"] = ("j")
    ipa_consonants["velar"] = ("k","ɡ","ŋ","x","ɣ")
    ipa_consonants["uvular"] = ()
    ipa_consonants["pharyngeal"] = ()
    ipa_consonants["glottal"] = ("ʔ","h")
    
    return ipa_consonants
    
def ipa_stress_dict():
    ipa_stress = {}
    ipa_stress["primary_stress"] = 'ˈ'
    ipa_stress["secondary_stress"] = 'ˌ'
    ipa_stress["long_vowel"] = 'ː'
    ipa_stress["english_button"] = '̩'
    return ipa_stress
