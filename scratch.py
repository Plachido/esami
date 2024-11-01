

# Example data
data = [
    (5, 'Cosa insegna Guetti?', 10, 'Religione', 0, 0),
    (5, 'Cosa insegna Guetti?', 11, 'Matematica', 1, 0),
    (5, 'Cosa insegna Guetti?', 12, 'Educazione Fisica', 0, 0),
    (4, 'Quale è la capitale della Francia?', 7, 'Parigi', 1, 1),
    (4, 'Quale è la capitale della Francia?', 8, 'Roma', 0, 1),
    (4, 'Quale è la capitale della Francia?', 9, 'Salerno', 0, 1)
]

# Restructuring the questions
questions = restructure_questions(data)

# Print the restructured questions
print(questions)
