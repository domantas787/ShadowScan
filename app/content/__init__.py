
#combines all the exercises


from app.content.network import NETWORK_EXERCISES
from app.content.injection import INJECTION_EXERCISES
from app.content.passwords import PASSWORD_EXERCISES
from app.content.malware import MALWARE_EXERCISES

ALL_EXERCISES = {
    **NETWORK_EXERCISES,
    **INJECTION_EXERCISES,
    **PASSWORD_EXERCISES,
    **MALWARE_EXERCISES,
}
