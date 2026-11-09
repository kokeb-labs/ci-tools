// Seeded violation: std::vector<bool> behind a type alias and as a class member.
#include <cstddef>
#include <vector>

namespace kv::rule_26_3_1::bad_alias {

using Flags = std::vector<bool>;

class Tracker {
 public:
  explicit Tracker(std::size_t n) : seen_(n, false) {}
  [[nodiscard]] std::size_t size() const { return seen_.size(); }

 private:
  std::vector<bool> seen_;  // seeded
};

std::size_t both() {
  Flags flags(3U, true);  // seeded
  flags[1] = false;
  return flags.size() + Tracker{2U}.size();
}

}  // namespace kv::rule_26_3_1::bad_alias
