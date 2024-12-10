#include <wx/wx.h>
#include "Networker.hh"
#include "MediaPlayer.hh"


class MainFrame : public wxFrame {
public:
    bool isHost{false};
    MainFrame() : wxFrame(nullptr, wxID_ANY, "Chat Application", wxDefaultPosition, wxSize(400, 600)) {
        networker.setDataCallback([this](jokinojo::ResponseData data) {
            wxTheApp->CallAfter([this, data]() {
                switch (data.datatype()){
                    case jokinojo::ResponseData_DataType_CREATE_ROOM:
                        wxMessageBox(wxString::Format(wxT("Room id is %i"),data.roomid()), "Incoming Data", wxOK | wxICON_INFORMATION, this);
                        isHost = true;
                        mediaPlayer->setIsHost(isHost);
                        break;
                    case jokinojo::ResponseData_DataType_JOIN_ROOM:
                        isHost = false;
                        mediaPlayer->setIsHost(isHost);
                        chatDisplay->AppendText("Connected\n");
                        chatDisplay->AppendText("Users in room:\n");
                        for (const std::string& username: data.usernames()) {
                            chatDisplay->AppendText(username + "\n");
                        }
                        break;
                    case jokinojo::ResponseData_DataType_USER_LEFT:
                        mediaPlayer->setMediaPausedStatus(true);
                        chatDisplay->AppendText(data.username() + " left\n");
                        break;
                    case jokinojo::ResponseData_DataType_SYNC:
                        mediaPlayer->setMediaStatus(!data.resumed(), data.timeposition());
                        chatDisplay->AppendText("Synchronized\n");
                        break;
                    case jokinojo::ResponseData_DataType_VIDEO_NAME:
                        wxMessageBox(wxString::Format(wxT("Video name is: %s\nYou can open via dragging the media file to the media player window."), data.videoname()), "Incoming Data", wxOK | wxICON_INFORMATION, this);
                        break;
                    case jokinojo::ResponseData_DataType_READY:
                        chatDisplay->AppendText(data.username() + " is ready\n");
                        break;
                    case jokinojo::ResponseData_DataType_CHAT:
                        chatDisplay->AppendText(data.username() + ": " + data.chatmessage() + "\n");
                        break;
                    case jokinojo::ResponseData_DataType_ERROR:
                        wxMessageBox(wxString::Format(wxT("Error: %s."), data.errormessage()), "Incoming Data", wxOK | wxICON_INFORMATION, this);
                        break;
                    case jokinojo::ResponseData_DataType_NULL_:
                        wxMessageBox(wxString::Format(wxT("Datatype Null came from server.")), "Incoming Data", wxOK | wxICON_INFORMATION, this);
                        break;
                    default:
                        wxMessageBox("i don't know this data", "Incoming Data", wxOK | wxICON_INFORMATION, this);
                }
            });
        });

        networker.initialize("0.0.0.0", 5000);
        std::thread networkIncomingHandlerThread(&Networker::handleIncomingData, &networker);
        networkIncomingHandlerThread.detach();
        mediaPlayer->initialize();


        // Create main sizer for the frame
        wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);

        // Initial setup
        loginPanel = new wxPanel(this);
        chatPanel = new wxPanel(this);
        chatPanel->Hide();  // Initially hide the chat panel

        // Nickname input panel
        nicknameLabel = new wxStaticText(loginPanel, wxID_ANY, "Enter Nickname:", wxPoint(20, 20));
        nicknameInput = new wxTextCtrl(loginPanel, wxID_ANY, "", wxPoint(20, 50), wxSize(200, -1));
        createButton = new wxButton(loginPanel, wxID_ANY, "Create Room", wxPoint(20, 90));
        joinButton = new wxButton(loginPanel, wxID_ANY, "Join Room", wxPoint(20, 140));

        // Chat interface panel
        chatDisplay = new wxTextCtrl(chatPanel, wxID_ANY, "", wxPoint(20, 20), wxSize(350, 400), wxTE_MULTILINE | wxTE_READONLY);
        chatInput = new wxTextCtrl(chatPanel, wxID_ANY, "", wxPoint(20, 430), wxSize(250, -1));
        sendButton = new wxButton(chatPanel, wxID_ANY, "Send", wxPoint(280, 430));

        // Add panels to main sizer
        mainSizer->Add(loginPanel, 1, wxEXPAND);
        mainSizer->Add(chatPanel, 1, wxEXPAND);

        // Set sizer for the frame
        SetSizer(mainSizer);

        // Event bindings
        createButton->Bind(wxEVT_BUTTON, &MainFrame::OnCreate, this);
        joinButton->Bind(wxEVT_BUTTON, &MainFrame::OnJoin, this);
        sendButton->Bind(wxEVT_BUTTON, &MainFrame::OnSendMessage, this);

    }

private:
    wxPanel* loginPanel;
    wxPanel* chatPanel;
    wxStaticText* nicknameLabel;
    wxTextCtrl* nicknameInput;
    wxButton* createButton;
    wxButton* joinButton;
    wxTextCtrl* chatDisplay;
    wxTextCtrl* chatInput;
    wxButton* sendButton;
    Networker& networker = Networker::get_instance();
    MediaPlayer* mediaPlayer = new MediaPlayer();

    void OnCreate(wxCommandEvent& event) {
        wxString username = nicknameInput->GetValue();

        if (username.IsEmpty()) {
            wxMessageBox("Please enter a username", "Error", wxOK | wxICON_ERROR);
            return;
        }
        networker.requestCreateRoom(username.ToStdString());

        loginPanel->Hide();
        chatPanel->Show();
        Layout();
        chatDisplay->AppendText("Connected as " + username + "\n");
    }

    void OnSendMessage(wxCommandEvent& event) {
        wxString message = chatInput->GetValue();
        if (message.IsEmpty()) return;

        networker.sendChatMessage(message.ToStdString());
        chatDisplay->AppendText("You: " + message + "\n");
        chatInput->Clear();
    }
    void OnJoin(wxCommandEvent& event) {
        wxString nickname = nicknameInput->GetValue();
        wxString roomId = wxGetTextFromUser(wxT("Enter Room ID:"), wxT("Room ID"));
        networker.requestJoinRoom(wxAtoi(roomId), nickname.ToStdString());
        loginPanel->Hide();
        chatPanel->Show();
        Layout();
    }
};

class App : public wxApp {
public:
    virtual bool OnInit() {
        MainFrame* frame = new MainFrame();
        frame->Show(true);
        return true;
    }
};

wxIMPLEMENT_APP(App);
