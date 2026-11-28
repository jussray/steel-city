#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "SteelCityPlayerController.generated.h"
class UUserWidget;
UCLASS()
class STEELCITY_API ASteelCityPlayerController : public APlayerController
{
    GENERATED_BODY()
protected:
    virtual void BeginPlay() override;
    UPROPERTY(EditDefaultsOnly, Category="Steel City|UI") TSubclassOf<UUserWidget> HUDWidgetClass;
    UPROPERTY(Transient) TObjectPtr<UUserWidget> HUDWidgetInstance;
};
