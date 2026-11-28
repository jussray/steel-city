#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SteelCityCombatComponent.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FSteelCityBlastRequested);
UCLASS(ClassGroup=(SteelCity), meta=(BlueprintSpawnableComponent))
class STEELCITY_API USteelCityCombatComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintAssignable, Category="Steel City|Combat") FSteelCityBlastRequested OnBlastRequested;
    UFUNCTION(BlueprintCallable, Category="Steel City|Combat") bool RequestBlast();
private:
    double NextBlastTime = 0.0;
};
