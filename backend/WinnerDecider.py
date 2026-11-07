# This file contains one class which is used to decide which object wins a fight
# returnWinner takes in two strings (which are the objects to be assessed), and returns the same string of the object which won the fight.
# Can take an optional parameter of a prompt used to tell instruct the AI.

try: #Checks if Ollama is installed
    import ollama
    from ollama import show
except:
    raise ImportError("Ollama needs to be installed through PiP.")

try: #Checks if the model is installed
    show("d3")
except:
    raise Exception("The d3 model needs to be installed on Ollama.")

class WinnerDecider:
    @staticmethod
    def returnWinner(object1:str, object2:str, prompt="Which object would win in a one-versus-one fight. Consider the physical properties of both objects.") -> str: #This method returns the object which will win in a fight
        response = ollama.systemone(
            model='d3',
            state=f'{object1}, {object2}',
            questions={
                'whoWins' : {
                    'type' : 'choice',
                    'instructions' : "Which object would win in a one-versus-one fight. Consider the physical properties of both objects.",
                    'criteria' : {
                        f"{object1}" : f"If {object1} wins the fight against {object2}",
                        f"{object2}" : f"If {object2} wins the fight against {object1}"
                    }
                }
            }
        )
        mostLikelyProbability = 0.0
        mostLikelyWinner = ""
        probabilities = response.answers['whoWins'].probabilities
        for key in probabilities: #This gets the most likely item to win in the dictionary
            if probabilities[key] > mostLikelyProbability:
                mostLikelyProbability = probabilities[key]
                mostLikelyWinner = key
        
        return mostLikelyWinner