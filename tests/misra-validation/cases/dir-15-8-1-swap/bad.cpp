// Seeded violation: a hand-written copy assignment that neither checks for self-assignment nor swaps.
#include <cstdint>

namespace kv::dir_15_8_1_swap::bad {

class Frame {
 public:
  Frame() = default;
  Frame(const Frame&) = default;
  Frame(Frame&&) noexcept = default;
  Frame& operator=(const Frame& other) {  // seeded
    length_ = 0U;
    length_ = other.length_;
    return *this;
  }
  Frame& operator=(Frame&&) noexcept = default;
  ~Frame() = default;

 private:
  std::uint32_t length_ = 0U;
};

}  // namespace kv::dir_15_8_1_swap::bad
