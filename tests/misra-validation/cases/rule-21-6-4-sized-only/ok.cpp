// Compliant: the sized and the unsized global operator delete are replaced together.
#include <cstddef>
#include <cstdlib>
#include <new>

void operator delete(void* block) noexcept { std::free(block); }

void operator delete(void* block, std::size_t size) noexcept {
  static_cast<void>(size);
  std::free(block);
}
