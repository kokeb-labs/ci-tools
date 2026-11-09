// Compliant: the unsized and the sized global operator delete replaced together in the same file.
#include <cstddef>
#include <cstdlib>
#include <new>

void operator delete(void* block) noexcept { std::free(block); }

void operator delete(void* block, std::size_t size) noexcept {
  static_cast<void>(size);
  std::free(block);
}
