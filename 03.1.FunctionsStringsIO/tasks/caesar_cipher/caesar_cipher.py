def encrypt(c: str, begin: int, key: int) -> str:
    """Encrypts symbol using caesar cipher

    :param c: what symbol to encrypt
    :param begin: ascii code of the first symbol in alphabet defining if symbol is lowercase or uppercase
    :param key: key of the cipher
    :return: encrypted symbol
    """
    alphabet_size = 26
    old_position = ord(c) - begin
    new_position = (old_position + key) % alphabet_size + begin
    return chr(new_position)


def caesar_encrypt(message: str, n: int) -> str:
    """Encrypt message using caesar cipher

    :param message: message to encrypt
    :param n: shift
    :return: encrypted message
    """
    lower_a_num = ord('a')
    upper_a_num = ord('A')
    res: list[str] = []
    for word in message.split():
        new_word: list[str] = []
        for symbol in word:
            if symbol.isalpha():
                new_word.append(encrypt(c=symbol,
                                        key=n,
                                        begin=upper_a_num if symbol.isupper() else lower_a_num))
            else:
                new_word.append(symbol)
        res.append(''.join(new_word))
    return ' '.join(res)
