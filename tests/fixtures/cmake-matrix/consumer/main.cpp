#include "ring/ring.hpp"

int main() {
  ring::Ring r;
  return (r.Push(1U) && (r.Size() == 1U)) ? 0 : 1;
}
