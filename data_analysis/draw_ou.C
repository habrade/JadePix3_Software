{
  //TFile* f1 = new TFile("Outfiles/total_x.root");
  TFile* f1 = new TFile("total_x_0to22.root");
  TH1F* th1resiXprojXall = (TH1F*) f1->Get("th1resiXprojXall");
  TCanvas* c1 = new TCanvas("c1","c1",0,0,800,600);
  th1resiXprojXall->Draw("HIST");
  th1resiXprojXall->GetXaxis()->SetTitle("Residual X (#mum)");
  th1resiXprojXall->GetYaxis()->SetTitle("Events");
  th1resiXprojXall->GetXaxis()->SetRangeUser(230,280);
  //th1resiXprojXall->Rebin(100);
  TLatex latex1;
  latex1.SetNDC();
  latex1.DrawLatex(0.68,0.8, "RMS = 5.63 #mum");
  c1->Update();
  c1->Print("Figures/th1resiXprojXall.pdf");

  TH1F* th1resiXprojXall_shift = new TH1F("th1resiXprojXall_shift","th1resiXprojXall_shift",100000,-500,500);
  double mean_th1resiXprojXall = th1resiXprojXall->GetMean();
  for(int i=1;i<=100000;i++){
    double bincenter = th1resiXprojXall->GetBinCenter(i);
    double bincontent = th1resiXprojXall->GetBinContent(i);
    th1resiXprojXall_shift->Fill(bincenter - mean_th1resiXprojXall, bincontent);
  }

  TCanvas* c1_shift = new TCanvas("c1_shift","c1_shift",0,0,800,600);
  th1resiXprojXall_shift->Draw("HIST");
  th1resiXprojXall_shift->GetXaxis()->SetTitle("Residual X (#mum)");
  th1resiXprojXall_shift->GetYaxis()->SetTitle("Events");
  th1resiXprojXall_shift->GetXaxis()->SetRangeUser(-25,25);
  //th1resiXprojXall_shift->Rebin(100);
  latex1.DrawLatex(0.68,0.8, "RMS = 5.63 #mum");
  c1_shift->Update();
  c1_shift->Print("Figures/th1resiXprojXall_shift.pdf");

  //TFile* f2 = new TFile("Output/total_0325_y.root");
  TFile* f2 = new TFile("total_y_595to610.root");
  TH1F* th1resiYprojYall = (TH1F*) f2->Get("th1resiYprojYall");
  TCanvas* c2 = new TCanvas("c2","c2",0,0,800,600);
  th1resiYprojYall->Draw("HIST");
  th1resiYprojYall->GetXaxis()->SetTitle("Residual Y (#mum)");
  th1resiYprojYall->GetYaxis()->SetTitle("Events");
  th1resiYprojYall->GetXaxis()->SetRangeUser(355,395);
  //th1resiYprojYall->Rebin(100);
  TLatex latex2;
  latex2.SetNDC();
  latex2.DrawLatex(0.68,0.8, "RMS = 4.03 #mum");
  c2->Update();  
  c1->Print("Figures/th1resiYprojYall.pdf");

  TH1F* th1resiYprojYall_shift = new TH1F("th1resiYprojYall_shift","th1resiYprojYall_shift",100000,-500,500);
  double mean_th1resiYprojYall = th1resiYprojYall->GetMean();
  for(int i=1;i<=100000;i++){
    double bincenter = th1resiYprojYall->GetBinCenter(i);
    double bincontent = th1resiYprojYall->GetBinContent(i);
    th1resiYprojYall_shift->Fill(bincenter - mean_th1resiYprojYall, bincontent);
  }

  TCanvas* c2_shift = new TCanvas("c2_shift","c2_shift",0,0,800,600);
  th1resiYprojYall_shift->Draw("HIST");
  th1resiYprojYall_shift->GetXaxis()->SetTitle("Residual Y (#mum)");
  th1resiYprojYall_shift->GetYaxis()->SetTitle("Events");
  th1resiYprojYall_shift->GetXaxis()->SetRangeUser(-20,20);
  //th1resiYprojYall_shift->Rebin(100);
  latex2.DrawLatex(0.68,0.8, "RMS = 4.03 #mum");
  c2_shift->Update();
  c2_shift->Print("Figures/th1resiYprojYall_shift.pdf");

  cout<<th1resiXprojXall->GetMean()<<" "<<th1resiXprojXall->GetRMS()<<" "<<th1resiXprojXall->GetEntries()<<endl;
  cout<<th1resiYprojYall->GetMean()<<" "<<th1resiYprojYall->GetRMS()<<" "<<th1resiYprojYall->GetEntries()<<endl;
 
  cout<<th1resiXprojXall_shift->GetMean()<<" "<<th1resiXprojXall_shift->GetRMS()<<" "<<th1resiXprojXall_shift->GetEntries()<<endl;
  cout<<th1resiYprojYall_shift->GetMean()<<" "<<th1resiYprojYall_shift->GetRMS()<<" "<<th1resiYprojYall_shift->GetEntries()<<endl; 
}
  
