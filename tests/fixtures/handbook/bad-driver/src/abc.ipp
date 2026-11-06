void F() {
  int* p = new int(1);
  delete p;
  throw 1;
}
