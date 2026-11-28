#pragma once
#include "CoreMinimal.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "SteelCityMovementComponent.generated.h"
UCLASS()
class STEELCITY_API USteelCityMovementComponent : public UCharacterMovementComponent
{
    GENERATED_BODY()
public:
    USteelCityMovementComponent();
    UFUNCTION(BlueprintCallable, Category="Steel City|Movement") void ToggleFlight();
};
