

## Test proportion of lines from the standard extraction in the json text file

def extract_comp(json,txt):
  "a simple comparison of json to txt"
  with open(json, "r") as f:
    brown_json = f.read()
  with open(txt, "r") as f:
    brown_txt = f.readlines()
  brown_set = {x[:-1] for x in brown_txt}
  test = [x for x in brown_set if x in brown_json]
  return len(test)/len(brown_set)

#[extract_comp(f"2020010300{x}.json",f"2020010300{x}.txt") for x in range(10,35)]