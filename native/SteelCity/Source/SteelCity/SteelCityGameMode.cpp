#include "SteelCityGameMode.h"
#include "SteelCityHero.h"
#include "SteelCityGameState.h"
#include "SteelCityPlayerController.h"
ASteelCityGameMode::ASteelCityGameMode()
{
    DefaultPawnClass = ASteelCityHero::StaticClass();
    GameStateClass = ASteelCityGameState::StaticClass();
    PlayerControllerClass = ASteelCityPlayerController::StaticClass();
}
