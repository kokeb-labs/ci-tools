// Seeded violation: a swap and a destructor that may throw.
#include <cstdint>

namespace kv::rule_18_4_1::bad_swap {

class Block {
 public:
  Block() = default;
  Block(const Block&) = default;
  Block(Block&&) noexcept = default;
  Block& operator=(const Block&) = default;
  Block& operator=(Block&&) noexcept = default;
  ~Block() noexcept(false) {}  // seeded

  void swap(Block& other) {  // seeded
    const std::uint32_t t = size_;
    size_ = other.size_;
    other.size_ = t;
  }

 private:
  std::uint32_t size_ = 0U;
};

}  // namespace kv::rule_18_4_1::bad_swap
