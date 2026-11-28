#include "SteelCityPlayerController.h"
#include "SteelCityHUD.h"
void ASteelCityPlayerController::BeginPlay()
{
    Super::BeginPlay();
    if (!IsLocalController() || HUDWidgetInstance) return;
    if (!HUDWidgetClass) HUDWidgetClass = USteelCityHUD::StaticClass();
    HUDWidgetInstance = CreateWidget<USteelCityHUD>(this, HUDWidgetClass);
    if (!HUDWidgetInstance) return;
    HUDWidgetInstance->AddToPlayerScreen();
    FInputModeGameAndUI Mode;
    SetInputMode(Mode);
}
