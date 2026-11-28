#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "SteelCityHUD.generated.h"
class UTextBlock;
class ASteelCityGameState;
UCLASS()
class STEELCITY_API USteelCityHUD : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
    UPROPERTY(meta=(BindWidget)) TObjectPtr<UTextBlock> StarCountText;
private:
    TWeakObjectPtr<ASteelCityGameState> BoundState;
    void RefreshBinding();
    void UnbindState();
    UFUNCTION() void HandleStarsChanged(int32 Count);
};
