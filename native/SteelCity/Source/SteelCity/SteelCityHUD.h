#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "SteelCityHUD.generated.h"
class UTextBlock;
class UButton;
class UImage;
class USteelCityJoystick;
class ASceneCapture2D;
class UTextureRenderTarget2D;
class ASteelCityHero;
class ASteelCityGameState;
UCLASS()
class STEELCITY_API USteelCityHUD : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    virtual void NativeConstruct() override;
    virtual void NativeDestruct() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
    UPROPERTY(meta=(BindWidget)) TObjectPtr<UTextBlock> StarCountText;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UButton> TalkButton;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UImage> MinimapImage;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UTextBlock> DialogueText;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<USteelCityJoystick> Joystick;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UButton> FlyButton;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UButton> BlastButton;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UButton> DownButton;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UButton> RunButton;
    UPROPERTY(meta=(BindWidgetOptional)) TObjectPtr<UButton> JumpButton;
private:
    UFUNCTION() void OnTalkClicked();
    void RefreshLocalWorldView(ASteelCityHero* Hero);
    void ReleaseMinimap();
    UPROPERTY(Transient) TObjectPtr<ASceneCapture2D> MinimapCapture;
    UPROPERTY(Transient) TObjectPtr<UTextureRenderTarget2D> MinimapTarget;
    float WorldViewTimer = 0.f;
    UFUNCTION() void OnFlyClicked();
    UFUNCTION() void OnBlastClicked();
    UFUNCTION() void OnDownPressed();
    UFUNCTION() void OnDownReleased();
    UFUNCTION() void OnRunPressed();
    UFUNCTION() void OnRunReleased();
    UFUNCTION() void OnJumpPressed();
    UFUNCTION() void OnJumpReleased();
    TWeakObjectPtr<ASteelCityHero> RunningHero;
    TWeakObjectPtr<ASteelCityHero> JumpingHero;
    float PreviousWalkSpeed = 600.f;
    bool bDownHeld = false;
    bool bRiseHeld = false;
    TWeakObjectPtr<ASteelCityGameState> BoundState;
    void RefreshBinding();
    void UnbindState();
    UFUNCTION() void HandleStarsChanged(int32 Count);
};
