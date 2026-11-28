#include "SteelCityPlayerController.h"
#include "Blueprint/UserWidget.h"
void ASteelCityPlayerController::BeginPlay()
{
    Super::BeginPlay();
    if (!IsLocalController() || !HUDWidgetClass || HUDWidgetInstance) return;
    HUDWidgetInstance = CreateWidget<UUserWidget>(this, HUDWidgetClass);
    if (!HUDWidgetInstance) return;
    HUDWidgetInstance->AddToPlayerScreen();
    FInputModeGameAndUI Mode;
    SetInputMode(Mode);
}
