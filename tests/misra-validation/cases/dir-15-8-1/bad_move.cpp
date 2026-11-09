// Seeded violation: a hand-written move assignment with no self-assignment handling.
#include <cstdint>

namespace kv::dir_15_8_1::bad_move {

class Frame {
 public:
  Frame() = default;
  Frame(const Frame&) = default;
  Frame(Frame&&) noexcept = default;
  Frame& operator=(const Frame&) = default;
  Frame& operator=(Frame&& other) noexcept {  // seeded
    length_ = other.length_;
    other.length_ = 0U;
    return *this;
  }
  ~Frame() = default;

 private:
  std::uint32_t length_ = 0U;
};

}  // namespace kv::dir_15_8_1::bad_move
