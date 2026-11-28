#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "SteelCityHero.generated.h"
class USpringArmComponent;
class UCameraComponent;
class USteelCityCombatComponent;
UCLASS()
class STEELCITY_API ASteelCityHero : public ACharacter
{
    GENERATED_BODY()
public:
    ASteelCityHero(const FObjectInitializer& ObjectInitializer);
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    UFUNCTION(BlueprintCallable, Category="Steel City|Input") void MoveForward(float Value);
    UFUNCTION(BlueprintCallable, Category="Steel City|Input") void MoveRight(float Value);
    UFUNCTION(BlueprintCallable, Category="Steel City|Input") void MoveVertical(float Value);
    UFUNCTION(BlueprintCallable, Category="Steel City|Input") void ToggleFlight();
    UFUNCTION(BlueprintCallable, Category="Steel City|Input") void Blast();
protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USpringArmComponent> CameraBoom;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UCameraComponent> FollowCamera;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USteelCityCombatComponent> CombatComponent;
};
