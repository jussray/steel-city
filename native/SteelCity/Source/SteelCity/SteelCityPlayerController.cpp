#include "SteelCityPlayerController.h"
#include "SteelCityHUD.h"
void ASteelCityPlayerController::BeginPlay()
{
    Super::BeginPlay();
    if (!IsLocalController() || !HUDWidgetClass || HUDWidgetInstance) return;
    HUDWidgetInstance = CreateWidget<USteelCityHUD>(this, HUDWidgetClass);
    if (!HUDWidgetInstance) return;
    HUDWidgetInstance->AddToPlayerScreen();
    FInputModeGameAndUI Mode;
    SetInputMode(Mode);
}
