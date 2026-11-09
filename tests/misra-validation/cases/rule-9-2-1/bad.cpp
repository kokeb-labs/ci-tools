// Seeded violation: a cast to a class type used as a whole statement; the temporary dies at once.
#include <cstdint>

namespace kv::rule_9_2_1::bad {

class Guard {
 public:
  explicit Guard(std::int32_t level) : level_(level) {}
  std::int32_t level() const { return level_; }

 private:
  std::int32_t level_;
};

std::int32_t enter(std::int32_t level) {
  static_cast<Guard>(level);
  return level;
}

}  // namespace kv::rule_9_2_1::bad
