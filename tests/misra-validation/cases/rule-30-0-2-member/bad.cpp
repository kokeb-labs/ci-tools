// Seeded violation: a stream member written straight after a read in a member function.
#include <fstream>

namespace kv::rule_30_0_2::bad_member {

class Store {
 public:
  explicit Store(std::fstream& file) : file_(file) {}
  void touch() {
    char c{};
    file_ >> c;
    file_ << c;  // seeded
  }

 private:
  std::fstream& file_;
};

}  // namespace kv::rule_30_0_2::bad_member
