#pragma once
#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "SteelCityInteractable.generated.h"
class ASteelCityHero;
UINTERFACE(BlueprintType)
class USteelCityInteractable : public UInterface
{
    GENERATED_BODY()
};
class STEELCITY_API ISteelCityInteractable
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Steel City|Interaction")
    FText Interact(ASteelCityHero* Hero);
};
