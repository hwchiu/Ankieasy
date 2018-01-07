isChinese = False

def GetCardType(models):
    global isChinese
    if models.byName('基本型') is not None:
        isChinese = True
        return "基本型"
    else:
        return "Basic"

def MakeCard(data):
    result = {}

    if 'front_word' not in data and 'back_word' not in data:
        return result
    if isChinese:
        result['正面'] = data['front_word']
        result['背面'] = data['back_word']
    else:
        result['Front'] = data['front_word']
        result['Back'] = data['back_word']
    return result
