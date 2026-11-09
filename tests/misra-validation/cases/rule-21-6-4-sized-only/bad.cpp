// Seeded violation: the sized global operator delete is replaced, the unsized one is not.
#include <cstddef>
#include <cstdlib>
#include <new>

void operator delete(void* block, std::size_t size) noexcept {
  static_cast<void>(size);
  std::free(block);
}
