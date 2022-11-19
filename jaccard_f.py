import random


def get_shingles(filename):

    comb = []

    with open(filename, 'r') as file:
        for line in file.readlines():
            comb.extend(line.split(' '))

    shingles = []

    for com in comb:
        shingles.append("".join(com))

    return shingles

def get_shingles_from_text(text):
    
    comb = []
    
    comb.extend(x.strip() for x in text.split(' '))
    
    shingles = []

    for com in comb:
        shingles.append("".join(com))

    return shingles


def get_matrix_dict(shingles_1, shingles_2):
    shin_dict = {}

    for hash1 in shingles_1:
        shin_dict[hash1] = [1, 0]

    for hash2 in shingles_2:
        if (shin_dict.get(hash2)):
            shin_dict[hash2] = [1, 1]
        else:
            shin_dict[hash2] = [0, 1]

    return shin_dict


def jaccard_similarity(shin_dict) -> None:

    print(shin_dict)

    intersected = 0
    union = len(shin_dict.keys())

    for v in shin_dict.values():
        if (v == [0, 0] or v == [1, 1]):
            intersected += 1

    with open('output.txt', 'w',encoding="utf-8") as file:
        for k in shin_dict.keys():
            file.write(f"{k} {shin_dict.get(k)[0]} {shin_dict.get(k)[1]}\n")

    print(f'intersection: {intersected}')
    print(f'union: {union}')

    return intersected / union


def get_min_hash(shin_dict, k=10):

    keys = shin_dict.keys()

    one_count = 0

    sign_matr = []

    for _ in range(k):

        temp = []
        temp.extend(keys)
        random.shuffle(temp)

        temp_count = get_single_min_hash(temp, shin_dict)

        sign_matr.append(get_signature_matrix(temp, shin_dict))

        print(f'for permutation {temp[:10]}: {temp_count}')
        one_count += temp_count

    print(f'Sign matrix: {sign_matr}')

    return one_count / k


def get_signature_matrix(keys, shin_dict):

    first = -1
    second = -1

    count = 0

    for k in keys:
        if not first >= 0:
            if shin_dict.get(k)[0] == 1:
                first = count

        if not second >= 0:
            if shin_dict.get(k)[1] == 1:
                second = count

        count += 1

        if first >= 0 and second >= 0:
            break

    return [first, second]


def get_single_min_hash(keys, shin_dict):

    for k in keys:
        if shin_dict.get(k)[0] == 1 or shin_dict.get(k)[1] == 1:
            return 1 if shin_dict.get(k)[0] == shin_dict.get(k)[1] else 0


def similarity(filename1, filename2):

    shingles_1 = get_shingles(filename1)
    shingles_2 = get_shingles(filename2)

    shin_dict = get_matrix_dict(shingles_1, shingles_2)

    jacc_sim = jaccard_similarity(shin_dict)

    min_hash_similarity = get_min_hash(shin_dict, 1000)

    print(f'Min hash similarity= {min_hash_similarity}')

    print(f'Jaccard similarity= {jacc_sim}')
    
def similarity_from_text(text1, text2):

    shingles_1 = get_shingles_from_text(text1)
    shingles_2 = get_shingles_from_text(text2)

    shin_dict = get_matrix_dict(shingles_1, shingles_2)

    jacc_sim = jaccard_similarity(shin_dict)

    min_hash_similarity = get_min_hash(shin_dict, 1000)

    print(f'Min hash similarity= {min_hash_similarity}')

    print(f'Jaccard similarity= {jacc_sim}')


if __name__ == "__main__":
    similarity("doc1", "doc2")
