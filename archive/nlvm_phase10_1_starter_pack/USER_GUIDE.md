# NLVM User Guide

Welcome to NLVM – the Natural Language Virtual Machine. You can now write and run programs using plain English!

## 🔧 How It Works
1. Write your code in English (`.nl` file)
2. Compile it using `nlp_compiler.py`
3. Run it using `nlvm.py`

## ✍️ Example Program
```
Set x to 5
Add x and 10 and store the result in total
Print total
```

## 🔍 Supported Commands (No Syntax Required!)
| Action | English Examples |
|--------|------------------|
| Set a variable | `Set x to 10`, `Create variable x and assign 20` |
| Add values | `Add x and y and store the result in z` |
| Print values | `Print z`, `Show me result`, `Display total` |
| Read file | `Read file data.txt and store lines in lines` |
| Write file | `Write Hello World to file output.txt` |
| Call API | `Call OpenWeather API with city as London and store temperature in temp` |

---

To run:
```
python nlp_compiler.py
python nlvm.py
```