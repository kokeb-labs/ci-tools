// Seeded violation: a functional-notation conversion to a class type (parentheses) used as a whole statement; the
// temporary dies at once. (Guard(level); alone would declare a variable named level.)
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
  Guard(level * 2);  // seeded
  return level;
}

}  // namespace kv::rule_9_2_1::bad
