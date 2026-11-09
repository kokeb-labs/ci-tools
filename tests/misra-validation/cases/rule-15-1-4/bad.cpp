// Seeded violation: a constructor that leaves a scalar member uninitialised.
#include <cstdint>

namespace kv::rule_15_1_4::bad {

class Channel {
 public:
  explicit Channel(std::uint8_t index) : index_(index) {}  // seeded

  [[nodiscard]] std::uint16_t gain() const { return gain_; }

 private:
  std::uint8_t index_;
  std::uint16_t gain_;
};

}  // namespace kv::rule_15_1_4::bad
