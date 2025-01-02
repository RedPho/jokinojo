#include <wx/wx.h>

#include <memory>
#include "Networker.hh"
#include "MediaPlayer.hh"

class MainFrame : public wxFrame {
public:
    MainFrame();

private:
    struct UIComponents {
        // Connection panel
        wxPanel* connectionPanel{nullptr};
        wxStaticText* ipLabel{nullptr};
        wxTextCtrl* ipInput{nullptr};
        wxStaticText* portLabel{nullptr};
        wxTextCtrl* portInput{nullptr};
        wxButton* connectButton{nullptr};

        // Login panel
        wxPanel* loginPanel{nullptr};
        wxStaticText* nicknameLabel{nullptr};
        wxTextCtrl* nicknameInput{nullptr};
        wxButton* createButton{nullptr};
        wxButton* joinButton{nullptr};

        // Chat panel
        wxPanel* chatPanel{nullptr};
        wxTextCtrl* chatDisplay{nullptr};
        wxTextCtrl* chatInput{nullptr};
        wxButton* sendButton{nullptr};
        wxButton* quitButton{nullptr};
    };

    UIComponents ui;
    bool isHost{false};
    bool inRoom{false};
    std::unique_ptr<MediaPlayer> mediaPlayer;
    std::unique_ptr<Networker> networker;

    // Init
    void initializeUI();
    void initializeConnectionPanel();
    void initializeLoginPanel();
    void initializeChatPanel();
    bool setupNetworking(const wxString& ip, long port);
    void bindEvents();
    void handleNetworkResponse(const jokinojo::ResponseData& data);
    void switchToLogin();
    void switchToChat();
    void switchToConnection();

    // Event handlers
    void OnConnect(wxCommandEvent& event);
    void OnCreate(wxCommandEvent& event);
    void OnJoin(wxCommandEvent& event);
    void OnSendMessage(wxCommandEvent& event);
    void OnQuit(wxCommandEvent& event);
    void OnClose(wxCloseEvent &event);

    // Network response handlers
    void handleCreateRoom(const jokinojo::ResponseData& data);
    void handleJoinRoom(const jokinojo::ResponseData& data);
    void handleUserLeft(const jokinojo::ResponseData& data);
    void handleSync(const jokinojo::ResponseData& data);
    void handleVideoName(const jokinojo::ResponseData& data);
    void handleReady(const jokinojo::ResponseData& data);
    void handleChat(const jokinojo::ResponseData& data);
    void handleError(const jokinojo::ResponseData& data);
    void handleNullResponse(const jokinojo::ResponseData& data);
};

MainFrame::MainFrame()
        : wxFrame(nullptr, wxID_ANY, "JoKinoJo", wxDefaultPosition, wxSize(400, 600))
        , networker(std::make_unique<Networker>())
        , mediaPlayer(std::make_unique<MediaPlayer>()) {
    initializeUI();
    bindEvents();
}

void MainFrame::initializeUI() {
    auto* mainSizer = new wxBoxSizer(wxVERTICAL);

    // Initialize all panels
    initializeConnectionPanel();
    initializeLoginPanel();
    initializeChatPanel();

    // Add panels to main sizer
    mainSizer->Add(ui.connectionPanel, 1, wxEXPAND);
    mainSizer->Add(ui.loginPanel, 1, wxEXPAND);
    mainSizer->Add(ui.chatPanel, 1, wxEXPAND);

    // Initially show only connection panel
    ui.loginPanel->Hide();
    ui.chatPanel->Hide();

    SetSizer(mainSizer);
}

void MainFrame::initializeConnectionPanel() {
    ui.connectionPanel = new wxPanel(this);
    auto* panelSizer = new wxBoxSizer(wxVERTICAL);

    // IP Address
    auto* ipSizer = new wxBoxSizer(wxHORIZONTAL);
    ui.ipLabel = new wxStaticText(ui.connectionPanel, wxID_ANY, "IP Address:");
    ui.ipInput = new wxTextCtrl(ui.connectionPanel, wxID_ANY, "127.0.0.1");
    ipSizer->Add(ui.ipLabel, 0, wxALL | wxALIGN_CENTER_VERTICAL, 5);
    ipSizer->Add(ui.ipInput, 1, wxALL, 5);

    // Port
    auto* portSizer = new wxBoxSizer(wxHORIZONTAL);
    ui.portLabel = new wxStaticText(ui.connectionPanel, wxID_ANY, "Port:");
    ui.portInput = new wxTextCtrl(ui.connectionPanel, wxID_ANY, "5000");
    portSizer->Add(ui.portLabel, 0, wxALL | wxALIGN_CENTER_VERTICAL, 5);
    portSizer->Add(ui.portInput, 1, wxALL, 5);

    // Connect button
    ui.connectButton = new wxButton(ui.connectionPanel, wxID_ANY, "Connect");

    // Add to panel sizer
    panelSizer->Add(ipSizer, 0, wxEXPAND | wxALL, 5);
    panelSizer->Add(portSizer, 0, wxEXPAND | wxALL, 5);
    panelSizer->Add(ui.connectButton, 0, wxALIGN_CENTER | wxALL, 5);

    ui.connectionPanel->SetSizer(panelSizer);
}

void MainFrame::initializeLoginPanel() {
    ui.loginPanel = new wxPanel(this);
    auto* panelSizer = new wxBoxSizer(wxVERTICAL);

    ui.nicknameLabel = new wxStaticText(ui.loginPanel, wxID_ANY, "Enter Nickname:");
    ui.nicknameInput = new wxTextCtrl(ui.loginPanel, wxID_ANY, "");
    ui.createButton = new wxButton(ui.loginPanel, wxID_ANY, "Create Room");
    ui.joinButton = new wxButton(ui.loginPanel, wxID_ANY, "Join Room");

    panelSizer->Add(ui.nicknameLabel, 0, wxALL, 5);
    panelSizer->Add(ui.nicknameInput, 0, wxEXPAND | wxALL, 5);
    panelSizer->Add(ui.createButton, 0, wxEXPAND | wxALL, 5);
    panelSizer->Add(ui.joinButton, 0, wxEXPAND | wxALL, 5);

    ui.loginPanel->SetSizer(panelSizer);
}

void MainFrame::initializeChatPanel() {
    ui.chatPanel = new wxPanel(this);
    auto* panelSizer = new wxBoxSizer(wxVERTICAL);

    ui.chatDisplay = new wxTextCtrl(ui.chatPanel, wxID_ANY, "",
                                    wxDefaultPosition, wxDefaultSize,
                                    wxTE_MULTILINE | wxTE_READONLY);

    auto* inputSizer = new wxBoxSizer(wxHORIZONTAL);
    ui.chatInput = new wxTextCtrl(ui.chatPanel, wxID_ANY, "");
    ui.sendButton = new wxButton(ui.chatPanel, wxID_ANY, "Send");
    ui.quitButton = new wxButton(ui.chatPanel, wxID_ANY, "Quit Room");  // Create the button here

    inputSizer->Add(ui.chatInput, 1, wxEXPAND | wxRIGHT, 5);
    inputSizer->Add(ui.sendButton, 0, wxEXPAND);

    panelSizer->Add(ui.chatDisplay, 1, wxEXPAND | wxALL, 5);
    panelSizer->Add(inputSizer, 0, wxEXPAND | wxALL, 5);
    panelSizer->Add(ui.quitButton, 0, wxEXPAND | wxALL, 5);

    ui.chatPanel->SetSizer(panelSizer);
}

void MainFrame::bindEvents() {
    ui.connectButton->Bind(wxEVT_BUTTON, &MainFrame::OnConnect, this);
    ui.createButton->Bind(wxEVT_BUTTON, &MainFrame::OnCreate, this);
    ui.joinButton->Bind(wxEVT_BUTTON, &MainFrame::OnJoin, this);
    ui.sendButton->Bind(wxEVT_BUTTON, &MainFrame::OnSendMessage, this);
    ui.quitButton->Bind(wxEVT_BUTTON, &MainFrame::OnQuit, this);
    ui.chatInput->Bind(wxEVT_TEXT_ENTER, &MainFrame::OnSendMessage, this);
    Bind(wxEVT_CLOSE_WINDOW, &MainFrame::OnClose, this);
}

void MainFrame::OnConnect(wxCommandEvent& event) {
    wxString ip = ui.ipInput->GetValue();
    long port;

    if (!ui.portInput->GetValue().ToLong(&port) || port <= 0 || port > 65535) {
        wxMessageBox("Invalid port number", "Error", wxOK | wxICON_ERROR);
        return;
    }

    if (ip.IsEmpty()) {
        wxMessageBox("Please enter an IP address", "Error", wxOK | wxICON_ERROR);
        return;
    }

    if (setupNetworking(ip, port)) {
        ui.connectionPanel->Hide();
        switchToLogin();
    }
}

bool MainFrame::setupNetworking(const wxString& ip, long port) {
    try {
        if (!networker->initialize(ip.ToStdString(), port)) {
            wxMessageBox(wxString::Format("Failed to initialize networker."),
                         "Connection Error", wxOK | wxICON_ERROR);
            return false;
        }
    } catch (const std::exception& e) {
        wxMessageBox(wxString::Format("Failed to connect: %s", e.what()),
                     "Connection Error", wxOK | wxICON_ERROR);
        return false;
    };
    networker->setDataCallback([this](jokinojo::ResponseData data) {
        wxTheApp->CallAfter([this, data]() {
            handleNetworkResponse(data);
        });
    });
    return true;


}

void MainFrame::handleNetworkResponse(const jokinojo::ResponseData& data) {
    switch (data.datatype()) {
        case jokinojo::ResponseData_DataType_CREATE_ROOM:
            handleCreateRoom(data);
            break;
        case jokinojo::ResponseData_DataType_JOIN_ROOM:
            handleJoinRoom(data);
            break;
        case jokinojo::ResponseData_DataType_USER_LEFT:
            handleUserLeft(data);
            break;
        case jokinojo::ResponseData_DataType_SYNC:
            handleSync(data);
            break;
        case jokinojo::ResponseData_DataType_VIDEO_NAME:
            handleVideoName(data);
            break;
        case jokinojo::ResponseData_DataType_READY:
            handleReady(data);
            break;
        case jokinojo::ResponseData_DataType_CHAT:
            handleChat(data);
            break;
        case jokinojo::ResponseData_DataType_ERROR:
            handleError(data);
            break;
        case jokinojo::ResponseData_DataType_NULL_:
            handleNullResponse(data);
            break;
        default:
            wxMessageBox("Unknown data type received", "Error", wxOK | wxICON_ERROR);
    }
}

void MainFrame::handleCreateRoom(const jokinojo::ResponseData& data) {
    inRoom = true;
    isHost = true;
    mediaPlayer->setIsHost(isHost);
    switchToChat();

    wxMessageBox(wxString::Format("Room id is %i", data.roomid()),
                 "Room Created", wxOK | wxICON_INFORMATION);

    ui.chatDisplay->AppendText( wxString::Format( wxString::Format("Created the room\nRoom id is %i\n", data.roomid()) ) );
    std::cout << "media player initializing.\n";
    mediaPlayer->initialize(networker.get());
    std::cout << "media player initialized.\n";
    std::thread mediaActionsHandlerThread(&MediaPlayer::handleMediaActions, mediaPlayer.get());
    mediaActionsHandlerThread.detach();
}

void MainFrame::handleJoinRoom(const jokinojo::ResponseData& data) {
    if (inRoom) {
        ui.chatDisplay->AppendText(data.username() + " is Connected\n");
        return;
    }

    inRoom = true;
    isHost = false;
    mediaPlayer->setIsHost(isHost);

    switchToChat();

    ui.chatDisplay->AppendText("Joined the room\n");
    ui.chatDisplay->AppendText("Users in room:\n");
    for (const auto& username : data.usernames()) {
        ui.chatDisplay->AppendText(username + "\n");
    }
    mediaPlayer->initialize(networker.get());

    std::thread mediaActionsHandlerThread(&MediaPlayer::handleMediaActions, mediaPlayer.get());
    mediaActionsHandlerThread.detach();

}

void MainFrame::handleUserLeft(const jokinojo::ResponseData& data) {
    mediaPlayer->setMediaPausedStatus(true);
    ui.chatDisplay->AppendText(data.username() + " left\n");
}

void MainFrame::handleSync(const jokinojo::ResponseData& data) {
    if (!isHost) {
        mediaPlayer->setMediaStatus(!data.resumed(), data.timeposition());
    }
}

void MainFrame::handleVideoName(const jokinojo::ResponseData& data) {
    if (isHost) {
        return;
    }
    wxMessageBox(
            wxString::Format("Video name is: %s\nYou can open via dragging the media file to the media player window.",
                             data.videoname()),
            "Video Information",
            wxOK | wxICON_INFORMATION
    );
    ui.chatDisplay->AppendText(wxString::Format("Video name is: %s\nYou can open via dragging the media file to the media player window.\n",data.videoname()));

}

void MainFrame::handleReady(const jokinojo::ResponseData& data) {
    ui.chatDisplay->AppendText(data.username() + " is ready\n");
}

void MainFrame::handleChat(const jokinojo::ResponseData& data) {
    ui.chatDisplay->AppendText(data.username() + ": " + data.chatmessage() + "\n");
}

void MainFrame::handleError(const jokinojo::ResponseData& data) {
    wxMessageBox(
            wxString::Format("Error: %s", data.errormessage()),
            "Error",
            wxOK | wxICON_ERROR
    );
}

void MainFrame::handleNullResponse(const jokinojo::ResponseData& data) {
    wxMessageBox("Received null response from server",
                 "Warning",
                 wxOK | wxICON_WARNING);
}

void MainFrame::switchToConnection() {
    ui.loginPanel->Hide();
    ui.chatPanel->Hide();
    ui.connectionPanel->Show();
    Layout();
}

void MainFrame::switchToLogin() {
    ui.loginPanel->Show();
    Layout();
}

void MainFrame::switchToChat() {
    ui.loginPanel->Hide();
    ui.chatPanel->Show();
    Layout();
}

void MainFrame::OnCreate(wxCommandEvent& event) {
    wxString username = ui.nicknameInput->GetValue();
    if (username.IsEmpty()) {
        wxMessageBox("Please enter a username", "Error", wxOK | wxICON_ERROR);
        return;
    }

    networker->requestCreateRoom(username.ToStdString());
}

void MainFrame::OnJoin(wxCommandEvent& event) {
    wxString nickname = ui.nicknameInput->GetValue();
    if (nickname.IsEmpty()) {
        wxMessageBox("Please enter a nickname", "Error", wxOK | wxICON_ERROR);
        return;
    }

    wxString roomId = wxGetTextFromUser("Enter Room ID:", "Room ID");
    if (!roomId.IsEmpty()) {
        long roomIdNum;
        if (!roomId.ToLong(&roomIdNum)) {
            wxMessageBox("Invalid room ID", "Error", wxOK | wxICON_ERROR);
            return;
        }
        networker->requestJoinRoom(roomIdNum, nickname.ToStdString());
    }
}

void MainFrame::OnSendMessage(wxCommandEvent& event) {
    wxString message = ui.chatInput->GetValue();
    if (!message.IsEmpty()) {
        networker->sendChatMessage(message.ToStdString());
        ui.chatInput->Clear();
    }
}

void MainFrame::OnQuit(wxCommandEvent& event) {
    if (networker && networker->isConnected()) {
        networker->requestQuit();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        networker = std::make_unique<Networker>(); // Destroy and create new instance

    }

    // Reset state
    inRoom = false;
    isHost = false;
    if (mediaPlayer) {
        mediaPlayer->stopMediaActions();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        mediaPlayer->destroy();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        mediaPlayer = std::make_unique<MediaPlayer>();

    }

    ui.chatDisplay->Clear();
    ui.loginPanel->Hide();
    ui.chatPanel->Hide();
    ui.nicknameInput->Clear();
    switchToConnection();
}


void MainFrame::OnClose(wxCloseEvent &event) {
    if (networker->isConnected()) {
        networker->requestQuit();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        networker->cleanup();
    }

    if (mediaPlayer) {
        mediaPlayer->destroy();
    }

    event.Skip();
}

class App : public wxApp {
public:
    bool OnInit() override {
        auto* frame = new MainFrame();
        frame->Show(true);
        return true;
    }
};

wxIMPLEMENT_APP(App);
