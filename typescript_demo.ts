// TypeScript Demo for Code Runner
// This file demonstrates TypeScript features

interface User {
    id: number;
    name: string;
    email: string;
    isActive: boolean;
}

class UserManager {
    private users: User[] = [];

    addUser(user: User): void {
        this.users.push(user);
        console.log(`✅ Added user: ${user.name}`);
    }

    getUserById(id: number): User | undefined {
        return this.users.find(user => user.id === id);
    }

    listActiveUsers(): User[] {
        return this.users.filter(user => user.isActive);
    }

    getUserCount(): number {
        return this.users.length;
    }
}

// Demo usage
function main(): void {
    console.log("🚀 TypeScript Code Runner Demo");
    console.log("=" .repeat(35));

    const userManager = new UserManager();

    // Add sample users
    const users: User[] = [
        { id: 1, name: "John Doe", email: "john@example.com", isActive: true },
        { id: 2, name: "Jane Smith", email: "jane@example.com", isActive: false },
        { id: 3, name: "Bob Johnson", email: "bob@example.com", isActive: true }
    ];

    users.forEach(user => userManager.addUser(user));

    console.log(`\n📊 Total users: ${userManager.getUserCount()}`);
    
    const activeUsers = userManager.listActiveUsers();
    console.log(`📈 Active users: ${activeUsers.length}`);
    
    activeUsers.forEach(user => {
        console.log(`   - ${user.name} (${user.email})`);
    });

    // Test user lookup
    const foundUser = userManager.getUserById(2);
    if (foundUser) {
        console.log(`\n🔍 Found user: ${foundUser.name} - ${foundUser.isActive ? 'Active' : 'Inactive'}`);
    }

    console.log("\n✅ TypeScript demo completed!");
}

main();