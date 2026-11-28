#include "SteelCityHUD.h"
#include "SteelCityGameState.h"
#include "Components/TextBlock.h"
#include "Engine/World.h"
#include "SteelCityHero.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/UniformGridPanel.h"
#include "Components/UniformGridSlot.h"
#include "Components/VerticalBox.h"
#include "Components/Border.h"
#include "Components/Image.h"
#include "SteelCityJoystick.h"
#include "Engine/SceneCapture2D.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Engine/TextureRenderTarget2D.h"

TSharedRef<SWidget> USteelCityHUD::RebuildWidget()
{
    // Blueprint-authored widget trees take priority. Native fallback has real controls,
    // not a simulated minimap or fictitious campaign progress.
    if (!WidgetTree) WidgetTree = NewObject<UWidgetTree>(this, TEXT("WidgetTree"), RF_Transient);
    if (WidgetTree && !WidgetTree->RootWidget)
    {
        UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("HUDRoot"));
        WidgetTree->RootWidget = Root;
        const FLinearColor Gold = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("FFC300")));
        const FLinearColor Cyan = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("00FFFF")));
        const FLinearColor Blue = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("1A2A40")));
        auto Text = [this](FName Name, const FText& Value, FLinearColor Color, int32 Size)
        {
            UTextBlock* Block = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Name);
            Block->SetText(Value);
            Block->SetColorAndOpacity(FSlateColor(Color));
            FSlateFontInfo Font = Block->GetFont();
            Font.Size = Size;
            Block->SetFont(Font);
            return Block;
        };
        UBorder* Counter = WidgetTree->ConstructWidget<UBorder>();
        Counter->SetBrushColor(Blue);
        UVerticalBox* CounterStack = WidgetTree->ConstructWidget<UVerticalBox>();
        Counter->SetContent(CounterStack);
        CounterStack->AddChildToVerticalBox(Text(TEXT("StarLabel"), NSLOCTEXT("SteelCity", "StarsLabel", "STEEL STARS"), Gold, 13));
        StarCountText = Text(TEXT("StarCountText"), NSLOCTEXT("SteelCity", "StarInitial", "0/5"), Gold, 32);
        CounterStack->AddChildToVerticalBox(StarCountText);
        UCanvasPanelSlot* CounterSlot = Root->AddChildToCanvas(Counter);
        CounterSlot->SetAnchors(FAnchors(1.f, 0.f));
        CounterSlot->SetAlignment(FVector2D(1.f, 0.f));
        CounterSlot->SetPosition(FVector2D(-20.f, 20.f));
        CounterSlot->SetAutoSize(true);
        UUniformGridPanel* Grid = WidgetTree->ConstructWidget<UUniformGridPanel>();
        Grid->SetMinDesiredSlotWidth(72.f);
        Grid->SetMinDesiredSlotHeight(56.f);
        Grid->SetSlotPadding(FMargin(3.f));
        auto Action = [&](FName Name, const FText& Label, int32 Row, int32 Col, FLinearColor Color)
        {
            UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), Name);
            Button->SetBackgroundColor(Blue);
            Button->SetContent(Text(FName(*(Name.ToString()+TEXT("Label"))), Label, Color, 12));
            Grid->AddChildToUniformGrid(Button, Row, Col);
            return Button;
        };
        TalkButton = Action(TEXT("TalkButton"), NSLOCTEXT("SteelCity", "Talk", "TALK"), 0, 0, Cyan);
        TalkButton->SetIsEnabled(false);
        FlyButton = Action(TEXT("FlyButton"), NSLOCTEXT("SteelCity", "Fly", "FLY"), 0, 1, Cyan);
        BlastButton = Action(TEXT("BlastButton"), NSLOCTEXT("SteelCity", "Blast", "BLAST"), 0, 2, Gold);
        DownButton = Action(TEXT("DownButton"), NSLOCTEXT("SteelCity", "Down", "DOWN"), 1, 0, Cyan);
        RunButton = Action(TEXT("RunButton"), NSLOCTEXT("SteelCity", "Run", "RUN"), 1, 1, Cyan);
        JumpButton = Action(TEXT("JumpButton"), NSLOCTEXT("SteelCity", "Jump", "JUMP"), 1, 2, Gold);
        UCanvasPanelSlot* GridSlot = Root->AddChildToCanvas(Grid);
        GridSlot->SetAnchors(FAnchors(1.f, 1.f));
        GridSlot->SetAlignment(FVector2D(1.f, 1.f));
        GridSlot->SetPosition(FVector2D(-20.f, -20.f));
        GridSlot->SetAutoSize(true);
        MinimapImage = WidgetTree->ConstructWidget<UImage>(UImage::StaticClass(),TEXT("MinimapImage"));
        MinimapImage->SetVisibility(ESlateVisibility::HitTestInvisible);
        UCanvasPanelSlot* MapSlot = Root->AddChildToCanvas(MinimapImage);
        MapSlot->SetPosition(FVector2D(20.f,20.f));
        MapSlot->SetSize(FVector2D(132.f,132.f));
        DialogueText = Text(TEXT("DialogueText"),FText::GetEmpty(),Cyan,14);
        DialogueText->SetVisibility(ESlateVisibility::HitTestInvisible);
        UCanvasPanelSlot* DialogueSlot = Root->AddChildToCanvas(DialogueText);
        DialogueSlot->SetAnchors(FAnchors(.5f,0.f));
        DialogueSlot->SetAlignment(FVector2D(.5f,0.f));
        DialogueSlot->SetPosition(FVector2D(0.f,28.f));
        DialogueSlot->SetAutoSize(true);
        Joystick = WidgetTree->ConstructWidget<USteelCityJoystick>(USteelCityJoystick::StaticClass(),TEXT("Joystick"));
        UCanvasPanelSlot* JoySlot = Root->AddChildToCanvas(Joystick);
        JoySlot->SetAnchors(FAnchors(0.f,1.f));
        JoySlot->SetAlignment(FVector2D(0.f,1.f));
        JoySlot->SetPosition(FVector2D(20.f,-20.f));
        JoySlot->SetSize(FVector2D(140.f,140.f));
    }
    return Super::RebuildWidget();
}

void USteelCityHUD::NativeConstruct()
{
    Super::NativeConstruct();
    RefreshBinding();
    if (TalkButton) TalkButton->OnClicked.AddUniqueDynamic(this,&USteelCityHUD::OnTalkClicked);
    if (FlyButton) FlyButton->OnClicked.AddUniqueDynamic(this, &USteelCityHUD::OnFlyClicked);
    if (BlastButton) BlastButton->OnClicked.AddUniqueDynamic(this, &USteelCityHUD::OnBlastClicked);
    if (DownButton) { DownButton->OnPressed.AddUniqueDynamic(this, &USteelCityHUD::OnDownPressed); DownButton->OnReleased.AddUniqueDynamic(this, &USteelCityHUD::OnDownReleased); }
    if (RunButton) { RunButton->OnPressed.AddUniqueDynamic(this, &USteelCityHUD::OnRunPressed); RunButton->OnReleased.AddUniqueDynamic(this, &USteelCityHUD::OnRunReleased); }
    if (JumpButton) { JumpButton->OnPressed.AddUniqueDynamic(this, &USteelCityHUD::OnJumpPressed); JumpButton->OnReleased.AddUniqueDynamic(this, &USteelCityHUD::OnJumpReleased); }
}
void USteelCityHUD::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    if (ASteelCityHero* Hero = Cast<ASteelCityHero>(GetOwningPlayerPawn()))
    {
        if (Joystick)
        {
            const FVector2D Axis=Joystick->GetJoystickInput();
            Hero->MoveForward(-Axis.Y); // screen up is forward
            Hero->MoveRight(Axis.X);
        }
        if (DialogueText && !DialogueText->GetText().EqualTo(Hero->LastDialogue)) DialogueText->SetText(Hero->LastDialogue);
        if (bDownHeld) Hero->MoveVertical(-1.f);
        if (bRiseHeld) Hero->MoveVertical(1.f);
    }
    WorldViewTimer -= InDeltaTime;
    if (WorldViewTimer<=0.f)
    {
        WorldViewTimer=.2f;
        RefreshLocalWorldView(Cast<ASteelCityHero>(GetOwningPlayerPawn()));
    }
    // State may arrive after a local widget is constructed or change during travel.
    RefreshBinding();
}
void USteelCityHUD::NativeDestruct()
{
    if (Joystick) Joystick->ResetInput();
    ReleaseMinimap();
    if (TalkButton) TalkButton->OnClicked.RemoveDynamic(this,&USteelCityHUD::OnTalkClicked);
    OnDownReleased(); OnRunReleased(); OnJumpReleased();
    if (FlyButton) FlyButton->OnClicked.RemoveDynamic(this, &USteelCityHUD::OnFlyClicked);
    if (BlastButton) BlastButton->OnClicked.RemoveDynamic(this, &USteelCityHUD::OnBlastClicked);
    if (DownButton) { DownButton->OnPressed.RemoveDynamic(this, &USteelCityHUD::OnDownPressed); DownButton->OnReleased.RemoveDynamic(this, &USteelCityHUD::OnDownReleased); }
    if (RunButton) { RunButton->OnPressed.RemoveDynamic(this, &USteelCityHUD::OnRunPressed); RunButton->OnReleased.RemoveDynamic(this, &USteelCityHUD::OnRunReleased); }
    if (JumpButton) { JumpButton->OnPressed.RemoveDynamic(this, &USteelCityHUD::OnJumpPressed); JumpButton->OnReleased.RemoveDynamic(this, &USteelCityHUD::OnJumpReleased); }
    UnbindState();
    Super::NativeDestruct();
}
void USteelCityHUD::UnbindState()
{
    if (ASteelCityGameState* State = BoundState.Get())
        State->OnStarsChanged.RemoveDynamic(this, &USteelCityHUD::HandleStarsChanged);
    BoundState.Reset();
}
void USteelCityHUD::RefreshBinding()
{
    ASteelCityGameState* State = GetWorld() ? GetWorld()->GetGameState<ASteelCityGameState>() : nullptr;
    if (State == BoundState.Get()) return;
    UnbindState();
    if (!State) return;
    BoundState = State;
    State->OnStarsChanged.AddUniqueDynamic(this, &USteelCityHUD::HandleStarsChanged);
    HandleStarsChanged(State->StarsCollected);
}
void USteelCityHUD::HandleStarsChanged(int32 Count)
{
    if (StarCountText)
        StarCountText->SetText(FText::Format(NSLOCTEXT("SteelCity", "StarCount", "{0}/{1}"),
            FText::AsNumber(Count), FText::AsNumber(FSteelCityStarLedger::Target)));
}

void USteelCityHUD::OnFlyClicked()
{
    if (ASteelCityHero* Hero = Cast<ASteelCityHero>(GetOwningPlayerPawn())) Hero->ToggleFlight();
}
void USteelCityHUD::OnBlastClicked()
{
    if (ASteelCityHero* Hero = Cast<ASteelCityHero>(GetOwningPlayerPawn())) Hero->Blast();
}
void USteelCityHUD::OnDownPressed() { bDownHeld = true; }
void USteelCityHUD::OnDownReleased() { bDownHeld = false; }
void USteelCityHUD::OnRunPressed()
{
    OnRunReleased();
    if (ASteelCityHero* Hero = Cast<ASteelCityHero>(GetOwningPlayerPawn()))
    {
        RunningHero = Hero;
        PreviousWalkSpeed = Hero->GetCharacterMovement()->MaxWalkSpeed;
        Hero->GetCharacterMovement()->MaxWalkSpeed = PreviousWalkSpeed * 1.7f;
    }
}
void USteelCityHUD::OnRunReleased()
{
    if (ASteelCityHero* Hero = RunningHero.Get()) Hero->GetCharacterMovement()->MaxWalkSpeed = PreviousWalkSpeed;
    RunningHero.Reset();
}
void USteelCityHUD::OnJumpPressed()
{
    OnJumpReleased();
    if (ASteelCityHero* Hero = Cast<ASteelCityHero>(GetOwningPlayerPawn()))
    {
        JumpingHero = Hero;
        if (Hero->GetCharacterMovement()->IsFlying()) bRiseHeld = true;
        else Hero->Jump();
    }
}
void USteelCityHUD::OnJumpReleased()
{
    bRiseHeld = false;
    if (ASteelCityHero* Hero = JumpingHero.Get()) Hero->StopJumping();
    JumpingHero.Reset();
}

void USteelCityHUD::OnTalkClicked()
{
    if (ASteelCityHero* Hero=Cast<ASteelCityHero>(GetOwningPlayerPawn())) Hero->Talk();
}
void USteelCityHUD::RefreshLocalWorldView(ASteelCityHero* Hero)
{
    if (TalkButton) TalkButton->SetIsEnabled(Hero && Hero->FindTalkTarget()!=nullptr);
    if (!MinimapImage || !Hero || !GetWorld() || !GetOwningPlayer() || !GetOwningPlayer()->IsLocalController()) return;
    if (!IsValid(MinimapCapture))
    {
        MinimapCapture=GetWorld()->SpawnActor<ASceneCapture2D>();
        if (!IsValid(MinimapCapture)) return;
        MinimapTarget=NewObject<UTextureRenderTarget2D>(this);
        MinimapTarget->InitAutoFormat(256,256);
        USceneCaptureComponent2D* Capture=MinimapCapture->GetCaptureComponent2D();
        Capture->TextureTarget=MinimapTarget;
        Capture->ProjectionType=ECameraProjectionMode::Orthographic;
        Capture->OrthoWidth=3000.f;
        Capture->bCaptureEveryFrame=false;
        Capture->bCaptureOnMovement=false;
        MinimapImage->SetBrushResourceObject(MinimapTarget);
    }
    MinimapCapture->SetActorLocationAndRotation(Hero->GetActorLocation()+FVector(0.f,0.f,3500.f),FRotator(-90.f,0.f,0.f));
    MinimapCapture->GetCaptureComponent2D()->CaptureScene();
}
void USteelCityHUD::ReleaseMinimap()
{
    if (MinimapImage) MinimapImage->SetBrushResourceObject(nullptr);
    if (IsValid(MinimapCapture)) MinimapCapture->Destroy();
    MinimapCapture=nullptr;
    MinimapTarget=nullptr;
}
