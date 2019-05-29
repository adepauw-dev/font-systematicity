from scipy.spatial.distance import directed_hausdorff, euclidean, hamming

class EditDistance():
    def get_distance(char1, char2):
        return hamming(char1, char2)
        
    def get_distances(chars1, chars2):
        if len(chars1) != len(chars2):
            raise Exception("Lists must be the same length.")
        return [get_distance(chars1[i], chars2[i]) for i in range(len(chars1))]

class EuclideanDistance():
    def get_distance(char1, char2):
        return euclidean(char1, char2)
        
    def get_distances(chars1, chars2):
        if len(chars1) != len(chars2):
            raise Exception("Lists must be the same length.")
        return [get_distance(chars1[i], chars2[i]) for i in range(len(chars1))]

class HaussdorffDistance():    
    def get_distance(char1, char2):
        return (directed_hausdorff(char1, char2), directed_hausdorff(char2, char1))
        
    def get_distances(chars1, chars2):
        if len(chars1) != len(chars2):
            raise Exception("Lists must be the same length.")
        return [get_distance(chars1[i], chars2[i]) for i in range(len(chars1))]