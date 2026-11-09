// Seeded violation: move constructor and move assignment without noexcept.
#include <cstdint>

namespace kv::rule_18_4_1::bad {

class Block {
 public:
  Block() = default;
  Block(const Block&) = default;
  Block(Block&& other) : size_(other.size_) {}
  Block& operator=(const Block&) = default;
  Block& operator=(Block&& other) {
    size_ = other.size_;
    return *this;
  }
  ~Block() = default;

 private:
  std::uint32_t size_ = 0U;
};

}  // namespace kv::rule_18_4_1::bad
