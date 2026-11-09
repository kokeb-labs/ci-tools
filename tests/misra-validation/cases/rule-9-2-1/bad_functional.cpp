// Seeded violation (functional): a functional-notation conversion to a class type as a whole statement.
#include <cstdint>

namespace kv::rule_9_2_1::bad_functional {

class Guard {
 public:
  explicit Guard(std::int32_t level) : level_(level) {}
  std::int32_t level() const { return level_; }

 private:
  std::int32_t level_;
};

std::int32_t enter(std::int32_t level) {
  Guard{level};
  return level;
}

}  // namespace kv::rule_9_2_1::bad_functional
