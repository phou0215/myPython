from collections import Counter


# count list엔 0 ~ 9 숫자가 들어있음.
count = [1,2,2,3,1,1,4,9,9,9,5,3,1]
result = Counter(count)
result = sorted(result.items(), key=lambda x:x[1], reverse=True)

print(result)
print(result[3][0])
