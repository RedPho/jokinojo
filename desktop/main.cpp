#include <wx/wx.h>

class MainFrame : public wxFrame {
public:
    MainFrame() : wxFrame(nullptr, wxID_ANY, "Chat Application", wxDefaultPosition, wxSize(400, 600)) {
        // Create main sizer for the frame
        wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);

        // Initial setup
        nicknamePanel = new wxPanel(this);
        chatPanel = new wxPanel(this);
        chatPanel->Hide();  // Initially hide the chat panel

        // Nickname input panel
        nicknameLabel = new wxStaticText(nicknamePanel, wxID_ANY, "Enter Nickname:", wxPoint(20, 20));
        nicknameInput = new wxTextCtrl(nicknamePanel, wxID_ANY, "", wxPoint(20, 50), wxSize(200, -1));
        createButton = new wxButton(nicknamePanel, wxID_ANY, "Create Room", wxPoint(20, 90));
        joinButton = new wxButton(nicknamePanel, wxID_ANY, "Join Room", wxPoint(20, 140));


        // Chat interface panel
        chatDisplay = new wxTextCtrl(chatPanel, wxID_ANY, "", wxPoint(20, 20), wxSize(350, 400), wxTE_MULTILINE | wxTE_READONLY);
        chatInput = new wxTextCtrl(chatPanel, wxID_ANY, "", wxPoint(20, 430), wxSize(250, -1));
        sendButton = new wxButton(chatPanel, wxID_ANY, "Send", wxPoint(280, 430));

        // Add panels to main sizer
        mainSizer->Add(nicknamePanel, 1, wxEXPAND);
        mainSizer->Add(chatPanel, 1, wxEXPAND);

        // Set sizer for the frame
        SetSizer(mainSizer);

        // Event bindings
        createButton->Bind(wxEVT_BUTTON, &MainFrame::OnCreate, this);
        joinButton->Bind(wxEVT_BUTTON, &MainFrame::OnJoin, this);

        sendButton->Bind(wxEVT_BUTTON, &MainFrame::OnSendMessage, this);
    }

private:
    wxPanel* nicknamePanel;
    wxPanel* chatPanel;
    wxStaticText* nicknameLabel;
    wxTextCtrl* nicknameInput;
    wxButton* createButton;
    wxButton* joinButton;
    wxTextCtrl* chatDisplay;
    wxTextCtrl* chatInput;
    wxButton* sendButton;

    void OnCreate(wxCommandEvent& event) {
        wxString nickname = nicknameInput->GetValue();

        if (nickname.IsEmpty()) {
            wxMessageBox("Please enter a nickname", "Error", wxOK | wxICON_ERROR);
            return;
        }

        nicknamePanel->Hide();
        chatPanel->Show();
        Layout();
        chatDisplay->AppendText("Connected as " + nickname + "\n");
    }

    void OnSendMessage(wxCommandEvent& event) {
        wxString message = chatInput->GetValue();
        if (message.IsEmpty()) return;

        chatDisplay->AppendText("You: " + message + "\n");
        chatInput->Clear();
    }
    void OnJoin(wxCommandEvent& event) {
        wxMessageBox("not implemented yet", "Error", wxOK | wxICON_ERROR);
    }
};

class ChatApp : public wxApp {
public:
    virtual bool OnInit() {
        MainFrame* frame = new MainFrame();
        frame->Show(true);
        return true;
    }
};

wxIMPLEMENT_APP(ChatApp);
