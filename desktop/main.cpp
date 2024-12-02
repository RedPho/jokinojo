#include <wx/wx.h>
#include "Networker.hh"


class MainFrame : public wxFrame {
public:
    bool isHost;
    MainFrame() : wxFrame(nullptr, wxID_ANY, "Chat Application", wxDefaultPosition, wxSize(400, 600)) {
        networker.initialize("0.0.0.0", 5000);
        std::thread networkIncomingHandlerThread(&Networker::handleIncomingData, &networker);
        networkIncomingHandlerThread.detach();

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

        chatDisplay->AppendText("You: " + message + "\n");
        chatInput->Clear();
    }
    void OnJoin(wxCommandEvent& event) {
        wxString nickname = nicknameInput->GetValue();
        wxString roomId = wxGetTextFromUser(wxT("Enter Room ID:"), wxT("Room ID"));
        //networker.requestJoinRoom(wxAtoi(roomId), nickname.ToStdString());
        wxMessageBox("roomID: " + roomId, "bu olay yerine join network olayi gerceklesecek", wxOK | wxICON_ERROR);
        loginPanel->Hide();
        chatPanel->Show();
        Layout();
        chatDisplay->AppendText("Connected as " + nickname + "\n");
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
