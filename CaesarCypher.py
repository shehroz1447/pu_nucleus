message = 'Shehroz Abdullah'

albhabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

shifted_alphabets = []
key = 4

for index, albhabet in enumerate(albhabets):

    if index + key > 25:
        index = index - 26

    shifted_alphabets[index] = albhabets[index + key]

    print (albhabets)



